#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys, time, unicodedata
from pathlib import Path
from typing import Any
from urllib import error, request

DATA = Path(__file__).with_name('malawi_service_details_v2_4.json')
COLLECTIONS = (
    "requirements",
    "fees",
    "faqs",
    "documents",
)


def norm(v: Any) -> str:
    return ' '.join(unicodedata.normalize('NFKD', str(v or '')).casefold().split())


def unpack(v: Any) -> list[dict[str, Any]]:
    if isinstance(v, list): return v
    if isinstance(v, dict):
        for k in ('value','data','items','results'):
            if isinstance(v.get(k), list): return v[k]
    return []


class API:
    def __init__(self, base_url: str, token: str | None):
        base = base_url.rstrip('/')
        self.root = base[:-7] if base.endswith('/api/v1') else base
        self.api = self.root + '/api/v1'
        self.token = token

    def call(self, method: str, path: str, payload: dict | None = None):
        url = path if path.startswith('http') else f"{self.api}/{path.lstrip('/')}"
        headers = {'Accept':'application/json'}
        if payload is not None: headers['Content-Type'] = 'application/json'
        if self.token: headers['Authorization'] = f'Bearer {self.token}'
        body = None if payload is None else json.dumps(payload).encode()
        req = request.Request(url, data=body, method=method, headers=headers)
        try:
            with request.urlopen(req, timeout=60) as r:
                raw = r.read().decode()
                return json.loads(raw) if raw else None
        except error.HTTPError as exc:
            raw = exc.read().decode(errors='replace')
            raise RuntimeError(f'{method} {url} -> HTTP {exc.code}: {raw}') from exc
        except error.URLError as exc:
            raise RuntimeError(f'{method} {url} failed: {exc.reason}') from exc

    def get(self, path: str): return self.call('GET', path)
    def post(self, path: str, payload: dict): return self.call('POST', path, payload)
    def spec(self): return self.call('GET', self.root + '/openapi.json')


def get_all(api: API, endpoint: str) -> list[dict]:
    rows, skip = [], 0
    while True:
        page = unpack(api.get(f'{endpoint}?skip={skip}&limit=100'))
        rows.extend(page)
        if len(page) < 100: return rows
        skip += len(page)


def resolve_schema(spec: dict, schema: dict) -> dict:
    if '$ref' in schema:
        name = schema['$ref'].split('/')[-1]
        return spec.get('components',{}).get('schemas',{}).get(name,{})
    return schema


def post_schema(spec: dict, endpoint: str) -> dict:
    path = '/api/v1/' + endpoint
    op = spec.get('paths',{}).get(path,{}).get('post')
    if not op: raise RuntimeError(f'OpenAPI does not expose POST {path}')
    schema = op.get('requestBody',{}).get('content',{}).get('application/json',{}).get('schema',{})
    return resolve_schema(spec, schema)


ALIASES = {
'requirements': {'title':('title','name','requirement'),'description':('description','details','notes'),'is_mandatory':('is_mandatory','required','is_required')},
'fees': {'name':('name','title','fee_name'),'amount':('amount','fee_amount'),'currency':('currency','fee_currency'),'description':('description','details','notes'),'is_mandatory':('is_mandatory','required','is_required')},
'faqs': {'question':('question','title'),'answer':('answer','description')},
'documents': {'name':('name','title','document_name'),'description':('description','details','notes'),'is_required':('is_required','required','is_mandatory'),'url':('file_url','url','download_url','document_url')},
'contacts': {'type':('type','contact_type'),'label':('label','name','title'),'value':('value','contact_value'),'is_primary':('is_primary','primary')},
'locations': {'name':('name','office_name','title'),'address':('address','street_address'),'city':('city',),'district':('district',),'country':('country',),'is_primary':('is_primary','primary')}
}


def adapt(collection: str, source: dict, schema: dict, service_id: int, agency_id: int) -> dict:
    props, required = schema.get('properties',{}), set(schema.get('required',[]))
    payload = {}
    if 'service_id' in props: payload['service_id'] = service_id
    if 'agency_id' in props: payload['agency_id'] = agency_id
    for canonical, candidates in ALIASES[collection].items():
        value = source.get(canonical)
        if value is None and canonical not in ('amount',): continue
        for candidate in candidates:
            if candidate in props:
                payload[candidate] = value
                break
    missing = [k for k in required if k not in payload]
    if missing:
        raise RuntimeError(f'{collection}: cannot satisfy required fields {missing}; OpenAPI fields={sorted(props)} source={source}')
    return payload


def fp(collection: str, x: dict) -> tuple:
    if collection == 'requirements': return (norm(x.get('title') or x.get('name') or x.get('requirement')),)
    if collection == 'fees': return (norm(x.get('name') or x.get('title')), str(x.get('amount') or x.get('fee_amount') or ''))
    if collection == 'faqs': return (norm(x.get('question') or x.get('title')),)
    if collection == 'documents': return (norm(x.get('name') or x.get('title')),)
    if collection == 'contacts': return (norm(x.get('type') or x.get('contact_type')), norm(x.get('value') or x.get('contact_value')))
    return (norm(x.get('name') or x.get('office_name')), norm(x.get('address')), norm(x.get('city')))


def detail_rows(details: dict, collection: str) -> list[dict]:
    keys = {'requirements':('requirement_items','requirements'),'fees':('fee_items','fees'),'faqs':('faq_items','faqs'),'documents':('document_items','documents')}
    if collection in keys:
        for k in keys[collection]:
            if isinstance(details.get(k), list): return details[k]
        return []
    return details.get(collection) if isinstance(details.get(collection), list) else []


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--base-url', required=True)
    p.add_argument('--token')
    p.add_argument('--apply', action='store_true')
    p.add_argument('--continue-on-error', action='store_true')
    p.add_argument('--data', default=str(DATA))
    a = p.parse_args()

    ds = json.loads(Path(a.data).read_text(encoding='utf-8'))
    api = API(a.base_url, a.token)
    spec = api.spec()
    schemas = {c: post_schema(spec,c) for c in COLLECTIONS}
    agencies, services = get_all(api,'agencies'), get_all(api,'services')
    agency_by_name = {norm(x.get('name')):x for x in agencies}
    services_by_key = {(int(x.get('agency_id') or 0),norm(x.get('name'))):x for x in services}
    stats = dict(services_found=0, services_missing=0, would_create=0, created=0, unchanged=0, failed=0, verified=0)

    print(f'Backend: {api.api}\nMode: {"APPLY" if a.apply else "DRY RUN"}')
    print(f'Dataset services: {len(ds.get("services",[]))}')
    print(f'Backend records: {len(agencies)} agencies, {len(services)} services')

    for profile in ds.get('services',[]):
        agency = agency_by_name.get(norm(profile.get('agency_name')))
        if not agency:
            stats['services_missing'] += 1; print('[missing-agency]', profile.get('agency_name')); continue
        service = services_by_key.get((int(agency['id']), norm(profile.get('service_name'))))
        if not service:
            stats['services_missing'] += 1; print('[missing-service]', profile.get('service_name'), '@', agency['name']); continue
        stats['services_found'] += 1
        details = api.get(f"services/{service['id']}/details")
        print(f"\n[service] id={service['id']} {service['name']} @ {agency['name']}")
        for collection in COLLECTIONS:
            existing = {fp(collection,row) for row in detail_rows(details,collection)}
            for source in profile.get(collection,[]):
                key = fp(collection,source)
                if key in existing:
                    stats['unchanged'] += 1; print(f'  [{collection}:exists] {key}'); continue
                try:
                    if (
                        collection == "fees"
                        and source.get("amount") is None
                    ):
                        print(
                            "  [fees:skipped-unknown-amount] "
                            f"{source.get('name', 'Unnamed fee')}"
                        )
                        continue

                    payload = adapt(
                        collection,
                        source,
                        schemas[collection],
                        int(service["id"]),
                        int(agency["id"]),
                    )
                    if a.apply:
                        api.post(collection,payload); stats['created'] += 1; print(f'  [{collection}:created] {payload}'); time.sleep(.05)
                    else:
                        stats['would_create'] += 1; print(f'  [{collection}:would-create] {payload}')
                except Exception as exc:
                    stats['failed'] += 1; print(f'  [{collection}:failed] {exc}', file=sys.stderr)
                    if not a.continue_on_error: raise
        if a.apply:
            verified = api.get(f"services/{service['id']}/details")
            counts = {
                c: len(detail_rows(verified, c))
                for c in COLLECTIONS
            }

            expected = {
                "requirements": len(profile.get("requirements", [])),
                "fees": sum(
                    1
                    for fee in profile.get("fees", [])
                    if fee.get("amount") is not None
                ),
                "faqs": len(profile.get("faqs", [])),
                "documents": len(profile.get("documents", [])),
            }

            verification_ok = all(
                counts[c] >= expected[c]
                for c in COLLECTIONS
            )

            if verification_ok:
                stats["verified"] += 1
                print(
                    "  [verified]",
                    {
                        "actual": counts,
                        "expected": expected,
                    },
                )
            else:
                stats["failed"] += 1
                print(
                    "  [verification-failed]",
                    {
                        "actual": counts,
                        "expected": expected,
                    },
                    file=sys.stderr,
                )

    print('\nStructured detail import summary')
    for k,v in stats.items(): print(f'{k}={v}')
    if not a.apply: print('Dry run complete. No records were changed.')
    return 0 if stats['failed'] == 0 else 2


if __name__ == '__main__': raise SystemExit(main())
