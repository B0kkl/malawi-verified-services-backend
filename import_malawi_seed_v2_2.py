#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,time,sys
from pathlib import Path
from urllib import request,error
DATA=Path(__file__).with_name("malawi_agencies_services_v2_2.json")
def norm(v):return re.sub(r"[^a-z0-9]+"," ",(v or "").lower()).strip()
class API:
    def __init__(self, b, t=None):
        self.base = b.rstrip("/")
        self.root = (
            self.base[:-7]
            if self.base.endswith("/api/v1")
            else self.base
        )
        self.api = (
            self.base
            if self.base.endswith("/api/v1")
            else self.base + "/api/v1"
        )
        self.t = t

    def call(self, m, u, p=None):
        body = None if p is None else json.dumps(p).encode()
        headers = {"Accept": "application/json"}

        if body is not None:
            headers["Content-Type"] = "application/json"

        if self.t:
            headers["Authorization"] = "Bearer " + self.t

        max_attempts = 6

        for attempt in range(1, max_attempts + 1):
            q = request.Request(
                u,
                data=body,
                method=m,
                headers=headers,
            )

            try:
                with request.urlopen(q, timeout=120) as response:
                    response_body = response.read().decode()
                    return (
                        json.loads(response_body)
                        if response_body
                        else None
                    )

            except error.HTTPError as exc:
                response_text = exc.read().decode(errors="replace")

                retryable_statuses = {
                    429,
                    500,
                    502,
                    503,
                    504,
                    520,
                    521,
                    522,
                    523,
                    524,
                }

                if exc.code in retryable_statuses:
                    if attempt == max_attempts:
                        raise RuntimeError(
                            f"{m} {u} -> HTTP {exc.code} after "
                            f"{max_attempts} attempts: {response_text}"
                        ) from exc

                    default_delay = (
                        60
                        if exc.code in {520, 521, 522, 523, 524}
                        else min(5 * attempt, 30)
                    )

                    retry_after = exc.headers.get("Retry-After")

                    try:
                        delay = max(
                            int(retry_after),
                            default_delay,
                        ) if retry_after else default_delay
                    except (TypeError, ValueError):
                        delay = default_delay

                    print(
                        f"[retry] {m} {u} returned HTTP {exc.code} "
                        f"(attempt {attempt}/{max_attempts}). "
                        f"Retrying in {delay} seconds..."
                    )

                    time.sleep(delay)
                    continue

                raise RuntimeError(
                    f"{m} {u} -> HTTP {exc.code}: "
                    f"{response_text}"
                )
            except (
                error.URLError,
                ConnectionResetError,
                TimeoutError,
                OSError,
            ) as exc:
                if attempt == max_attempts:
                    raise RuntimeError(
                        f"{m} {u} failed after "
                        f"{max_attempts} attempts: {exc}"
                    ) from exc

                delay = min(5 * attempt, 30)

                print(
                    f"[retry] {m} {u} failed "
                    f"(attempt {attempt}/{max_attempts}): {exc}. "
                    f"Retrying in {delay} seconds..."
                )

                time.sleep(delay)

    def get(self, p):
        return self.call("GET", self.api + "/" + p)

    def get_all(self, resource, page_size=100):
        records = []
        skip = 0
        seen_ids = set()

        while True:
            separator = "&" if "?" in resource else "?"

            page = listv(
                self.get(
                    f"{resource}{separator}"
                    f"skip={skip}&limit={page_size}"
                )
            )

            if not page:
                break

            new_records = []

            for record in page:
                record_id = record.get("id")

                if record_id is None or record_id not in seen_ids:
                    new_records.append(record)

                    if record_id is not None:
                        seen_ids.add(record_id)

            if not new_records:
                print(
                    f"[pagination] {resource}: "
                    "no new records returned; stopping"
                )
                break

            records.extend(new_records)
            skip += len(page)

            print(
                f"[pagination] {resource}: "
                f"page={len(page)}, "
                f"total={len(records)}, "
                f"next_skip={skip}"
            )

        return records

    def post(self, p, d):
        return self.call("POST", self.api + "/" + p, d)

    def spec(self):
        return self.call(
            "GET",
            self.root + "/openapi.json"
        )
def listv(v):
    if isinstance(v,list):return v
    for k in ("data","items","results"):
        if isinstance(v,dict) and isinstance(v.get(k),list):return v[k]
    raise RuntimeError("Expected list response")
def obj(v):return v["data"] if isinstance(v,dict) and isinstance(v.get("data"),dict) else v
def fields(sp,path):
    s=sp["paths"][path]["post"]["requestBody"]["content"]["application/json"]["schema"]
    if "$ref" in s:
        x=sp
        for p in s["$ref"].lstrip("#/").split("/"):x=x[p]
        s=x
    return set(s.get("properties",{}))
def clean(d,f):return {k:v for k,v in d.items() if k in f and v not in (None,"")}
def main():
    p=argparse.ArgumentParser();p.add_argument("--base-url",required=True);p.add_argument("--token")
    p.add_argument("--apply",action="store_true");p.add_argument("--continue-on-error",action="store_true")
    a=p.parse_args();ds=json.loads(DATA.read_text(encoding="utf-8"));api=API(a.base_url,a.token)
    sp=api.spec();af=fields(sp,"/api/v1/agencies");sf=fields(sp,"/api/v1/services")
    print(f"Backend: {a.base_url}\nMode: {'APPLY' if a.apply else 'DRY RUN'}")
    print(f"Dataset: {len(ds['agencies'])} agencies, {len(ds['services'])} services")
    old=api.get_all("agencies");by={norm(x.get("name","")):x for x in old};ids={}
    ca=sa=fa=0
    for x in ds["agencies"]:
        e=by.get(norm(x["name"]))
        if e:ids[x["key"]]=int(e["id"]);sa+=1;print(f"[agency:exists] {x['name']} -> id={e['id']}");continue
        d=clean({k:x.get(k) for k in ("name","short_name","category","description","website","city","country","is_active")},af)
        if not a.apply:print(f"[agency:would-create] {x['name']} payload={d}");continue
        try:
            n=obj(api.post("agencies",d));ids[x["key"]]=int(n["id"]);by[norm(x["name"])]=n;ca+=1
            print(f"[agency:created] {x['name']} -> id={n['id']}");time.sleep(.08)
        except Exception as ex:
            if "HTTP 409" in str(ex):
                sa += 1
                print(
                    f"[agency:exists] {x['name']} "
                    "-> duplicate reported by API"
                )
                continue

            fa += 1
            print(
                f"[agency:failed] {x['name']}: {ex}",
                file=sys.stderr,
            )

            if not a.continue_on_error:
                raise
    if not a.apply:
        print("\nDry run complete. No records were written.");return 0
    old_s=api.get_all("services");keys={(norm(x.get("name","")),int(x.get("agency_id") or 0)) for x in old_s}
    cs=ss=fs=0
    for x in ds["services"]:
        aid=ids.get(x["agency_key"])
        if not aid:fs+=1;print(f"[service:no-agency] {x['name']}",file=sys.stderr);continue
        key=(norm(x["name"]),aid)
        if key in keys:ss+=1;print(f"[service:exists] {x['name']} -> agency_id={aid}");continue
        d=clean({"agency_id":aid,"name":x.get("name"),"description":x.get("description"),
        "category":x.get("category"),"requirements":x.get("requirements"),
        "application_process":x.get("application_process"),"processing_time":x.get("processing_time"),
        "fee_amount":x.get("fee_amount"),"fee_currency":x.get("fee_currency"),
        "office_location":x.get("office_location"),"contact_email":x.get("contact_email"),
        "contact_phone":x.get("contact_phone"),"online_available":x.get("online_available"),
        "online_url":x.get("online_url"),"is_active":x.get("is_active",True)},sf)
        try:
            n=obj(api.post("services",d));keys.add(key);cs+=1
            print(f"[service:created] {x['name']} -> id={n.get('id')} agency_id={aid}");time.sleep(.08)
        except Exception as ex:
            if "HTTP 409" in str(ex):
                keys.add(key)
                ss += 1
                print(
                    f"[service:exists] {x['name']} "
                    f"-> agency_id={aid} "
                    "duplicate reported by API"
                )
                continue

            fs += 1
            print(
                f"[service:failed] {x['name']}: {ex}",
                file=sys.stderr,
            )

            if not a.continue_on_error:
                raise
    print(f"\nAgencies created={ca}, existed={sa}, failed={fa}")
    print(f"Services created={cs}, existed={ss}, failed={fs}")
    return 0 if fa==0 and fs==0 else 2
if __name__=="__main__":raise SystemExit(main())


