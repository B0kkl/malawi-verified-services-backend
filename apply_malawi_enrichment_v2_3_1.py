#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,sys,time
from pathlib import Path
from urllib import request,error

DATA=Path(__file__).with_name("malawi_enrichment_v2_3.json")
def norm(v): return re.sub(r"[^a-z0-9]+"," ",(v or "").lower()).strip()

class API:
    def __init__(self,base,token=None):
        self.base=base.rstrip("/")
        self.root=self.base[:-7] if self.base.endswith("/api/v1") else self.base
        self.api=self.base if self.base.endswith("/api/v1") else self.base+"/api/v1"
        self.token=token
    def call(self,method,url,payload=None):
        body=None if payload is None else json.dumps(payload).encode()
        h={"Accept":"application/json"}
        if body is not None:h["Content-Type"]="application/json"
        if self.token:h["Authorization"]="Bearer "+self.token
        req=request.Request(url,data=body,method=method,headers=h)
        try:
            with request.urlopen(req,timeout=120) as r:
                raw=r.read().decode()
                return json.loads(raw) if raw else None
        except error.HTTPError as e:
            raise RuntimeError(f"{method} {url} -> HTTP {e.code}: {e.read().decode(errors='replace')}")
    def get(self,path):return self.call("GET",self.api+"/"+path.lstrip("/"))
    def patch(self,path,payload):return self.call("PATCH",self.api+"/"+path.lstrip("/"),payload)
    def post(self,path,payload):return self.call("POST",self.api+"/"+path.lstrip("/"),payload)
    def spec(self):return self.call("GET",self.root+"/openapi.json")

def listv(v):
    if isinstance(v,list):return v
    if isinstance(v,dict):
        for k in ("data","items","results"):
            if isinstance(v.get(k),list):return v[k]
    raise RuntimeError("Expected list response")

def get_all(api,path,page_size=100):
    """Fetch every page from list endpoints using skip/limit pagination."""
    rows=[]
    skip=0
    seen_ids=set()
    while True:
        sep="&" if "?" in path else "?"
        batch=listv(api.get(f"{path}{sep}skip={skip}&limit={page_size}"))
        if not batch:
            break

        added=0
        for row in batch:
            rid=row.get("id") if isinstance(row,dict) else None
            marker=("id",rid) if rid is not None else ("row",repr(row))
            if marker in seen_ids:
                continue
            seen_ids.add(marker)
            rows.append(row)
            added+=1

        if len(batch) < page_size:
            break
        if added == 0:
            raise RuntimeError(
                f"Pagination for {path} did not advance at skip={skip}. "
                "Confirm that the endpoint supports skip and limit."
            )
        skip += page_size
    return rows

def schema_fields(spec,path,method):
    op=spec.get("paths",{}).get(path,{}).get(method.lower())
    if not op:return None
    s=op.get("requestBody",{}).get("content",{}).get("application/json",{}).get("schema",{})
    if "$ref" in s:
        node=spec
        for p in s["$ref"].lstrip("#/").split("/"):node=node[p]
        s=node
    return set(s.get("properties",{})) or None

def clean(d,fields):
    d={k:v for k,v in d.items() if v not in (None,"")}
    return d if fields is None else {k:v for k,v in d.items() if k in fields}

def changed(existing,patch):
    return {k:v for k,v in patch.items() if existing.get(k)!=v}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--base-url",required=True);p.add_argument("--token")
    p.add_argument("--apply",action="store_true")
    p.add_argument("--continue-on-error",action="store_true")
    a=p.parse_args()
    ds=json.loads(DATA.read_text(encoding="utf-8"))
    api=API(a.base_url,a.token);sp=api.spec()

    af=schema_fields(sp,"/api/v1/agencies/{agency_id}","patch")
    sf=schema_fields(sp,"/api/v1/services/{service_id}","patch")
    scf=schema_fields(sp,"/api/v1/services","post")
    if af is None:raise RuntimeError("Backend OpenAPI does not expose PATCH /api/v1/agencies/{agency_id}")
    if sf is None:raise RuntimeError("Backend OpenAPI does not expose PATCH /api/v1/services/{service_id}")

    agencies=get_all(api,"agencies")
    services=get_all(api,"services")
    print(f"Loaded existing records: {len(agencies)} agencies, {len(services)} services")
    agency_by_name={norm(x.get("name","")):x for x in agencies}
    services_by_key={(int(x.get("agency_id") or 0),norm(x.get("name",""))):x for x in services}

    print(f"Backend: {a.base_url}")
    print(f"Mode: {'APPLY' if a.apply else 'DRY RUN'}")
    print(f"Agency enrichment profiles: {len(ds['agency_enrichments'])}")
    print(f"Specific service enrichments: {len(ds['service_enrichments'])}")

    stats={"agency_updated":0,"agency_unchanged":0,"agency_missing":0,
           "service_updated":0,"service_unchanged":0,"service_created":0,
           "service_missing":0,"failed":0}

    for profile in ds["agency_enrichments"]:
        agency=agency_by_name.get(norm(profile["agency_name"]))
        if not agency:
            stats["agency_missing"]+=1
            print(f"[agency:missing] {profile['agency_name']}")
            continue
        patch=clean(profile.get("agency_patch",{}),af)
        delta=changed(agency,patch)
        if delta:
            print(f"[agency:{'update' if a.apply else 'would-update'}] {agency['name']} delta={delta}")
            if a.apply:
                try:
                    api.patch(f"agencies/{agency['id']}",delta);stats["agency_updated"]+=1;agency.update(delta);time.sleep(.05)
                except Exception as ex:
                    stats["failed"]+=1;print(f"[agency:failed] {agency['name']}: {ex}",file=sys.stderr)
                    if not a.continue_on_error:raise
        else:stats["agency_unchanged"]+=1

        defaults=profile.get("service_defaults",{})
        overrides=profile.get("service_overrides",{})
        for (aid,sname),svc in list(services_by_key.items()):
            if aid!=int(agency["id"]):continue
            merged=dict(defaults);merged.update(overrides.get(svc.get("name",""),{}))
            patch=clean(merged,sf);delta=changed(svc,patch)
            if not delta:stats["service_unchanged"]+=1;continue
            print(f"[service:{'update' if a.apply else 'would-update'}] {svc['name']} @ {agency['name']} delta={delta}")
            if a.apply:
                try:
                    api.patch(f"services/{svc['id']}",delta);stats["service_updated"]+=1;svc.update(delta);time.sleep(.04)
                except Exception as ex:
                    stats["failed"]+=1;print(f"[service:failed] {svc['name']}: {ex}",file=sys.stderr)
                    if not a.continue_on_error:raise

    for item in ds["service_enrichments"]:
        agency=agency_by_name.get(norm(item["agency_name"]))
        if not agency:
            stats["service_missing"]+=1;print(f"[specific:no-agency] {item['agency_name']}");continue
        key=(int(agency["id"]),norm(item["service_name"]))
        svc=services_by_key.get(key)
        if svc:
            patch=clean(item["patch"],sf);delta=changed(svc,patch)
            if not delta:stats["service_unchanged"]+=1;continue
            print(f"[specific:{'update' if a.apply else 'would-update'}] {item['service_name']} delta={delta}")
            if a.apply:
                try:
                    api.patch(f"services/{svc['id']}",delta);stats["service_updated"]+=1;svc.update(delta);time.sleep(.04)
                except Exception as ex:
                    stats["failed"]+=1;print(f"[specific:failed] {item['service_name']}: {ex}",file=sys.stderr)
                    if not a.continue_on_error:raise
        else:
            payload={"agency_id":agency["id"],"name":item["service_name"],**item["patch"],"is_active":True}
            payload=clean(payload,scf)
            print(f"[specific:{'create' if a.apply else 'would-create'}] {item['service_name']} payload={payload}")
            if a.apply:
                try:
                    new=api.post("services",payload);stats["service_created"]+=1;time.sleep(.04)
                except Exception as ex:
                    stats["failed"]+=1;print(f"[specific:create-failed] {item['service_name']}: {ex}",file=sys.stderr)
                    if not a.continue_on_error:raise

    print("\nEnrichment summary")
    for k,v in stats.items():print(f"{k}={v}")
    if not a.apply:print("Dry run complete. No records were changed.")
    return 0 if stats["failed"]==0 else 2

if __name__=="__main__":raise SystemExit(main())
