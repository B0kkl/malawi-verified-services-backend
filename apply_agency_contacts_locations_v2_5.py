from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any
from urllib import error, parse, request


DATA_FILE = Path("malawi_service_details_v2_4.json")

CONTACT_ENDPOINT = "contacts"
LOCATION_ENDPOINT = "locations"


def normalise(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


class ApiClient:
    def __init__(self, base_url: str) -> None:
        base = base_url.rstrip("/")

        if not base.endswith("/api/v1"):
            base = f"{base}/api/v1"

        self.base_url = base

    def call(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"

        if query:
            url = f"{url}?{parse.urlencode(query)}"

        body = None
        headers = {"Accept": "application/json"}

        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = request.Request(
            url,
            data=body,
            method=method,
            headers=headers,
        )

        try:
            with request.urlopen(req, timeout=60) as response:
                raw = response.read().decode("utf-8")

                if not raw:
                    return None

                return json.loads(raw)

        except error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"{method} {url} -> HTTP {exc.code}: {raw}"
            ) from exc

        except error.URLError as exc:
            raise RuntimeError(
                f"{method} {url} -> network error: {exc}"
            ) from exc

    def get_all(self, path: str) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        skip = 0
        limit = 100

        while True:
            result = self.call(
                "GET",
                path,
                query={
                    "skip": skip,
                    "limit": limit,
                },
            )

            if isinstance(result, list):
                batch = result
            elif isinstance(result, dict):
                batch = (
                    result.get("items")
                    or result.get("data")
                    or result.get("results")
                    or []
                )
            else:
                batch = []

            records.extend(batch)

            if len(batch) < limit:
                break

            skip += limit

        return records

    def post(
        self,
        path: str,
        payload: dict[str, Any],
    ) -> Any:
        return self.call("POST", path, payload=payload)


def build_contact_payload(
    agency_id: int,
    source: dict[str, Any],
    agency_name: str,
) -> dict[str, Any] | None:
    contact_type = normalise(source.get("type"))
    label = str(source.get("label") or agency_name).strip()
    value = str(source.get("value") or "").strip()

    if not value:
        return None

    payload: dict[str, Any] = {
        "agency_id": agency_id,
        "full_name": label,
        "department": agency_name,
        "is_primary": bool(source.get("is_primary", False)),
        "is_active": True,
    }

    if contact_type == "phone":
        # Preserve multiple published numbers as one official contact value.
        payload["phone_number"] = value
        payload["notes"] = "Official agency telephone contact."

    elif contact_type == "email":
        payload["email"] = value
        payload["notes"] = "Official agency email contact."

    elif contact_type == "website":
        # The backend contact model has no website field.
        # Preserve the official URL in notes rather than misusing email/phone.
        payload["notes"] = f"Official website: {value}"

    else:
        payload["notes"] = f"Official contact information: {value}"

    return payload


def build_location_payload(
    agency_id: int,
    source: dict[str, Any],
    agency_name: str,
) -> dict[str, Any] | None:
    name = str(source.get("name") or "").strip()
    address = str(source.get("address") or "").strip()
    city = str(source.get("city") or "").strip()
    district = str(source.get("district") or "").strip()

    # This is a web service, not a physical agency office.
    if normalise(name) == "online evisa service":
        return None

    if not district:
        return None

    postal_address = None
    physical_address = address

    # Treat PO Box-only values as postal addresses.
    if normalise(address).startswith("p.o. box"):
        postal_address = address
        physical_address = ", ".join(
            part
            for part in (
                agency_name,
                city or district,
                "Malawi",
            )
            if part
        )

    if city and normalise(city) not in normalise(physical_address):
        physical_address = f"{physical_address}, {city}"

    if not physical_address:
        return None

    return {
        "agency_id": agency_id,
        "physical_address": physical_address,
        "district": district,
        "postal_address": postal_address,
        "is_head_office": bool(source.get("is_primary", False)),
    }


def contact_key(payload: dict[str, Any]) -> tuple[str, ...]:
    return (
        str(payload.get("agency_id")),
        normalise(payload.get("full_name")),
        normalise(payload.get("phone_number")),
        normalise(payload.get("email")),
        normalise(payload.get("notes")),
    )


def location_key(payload: dict[str, Any]) -> tuple[str, ...]:
    return (
        str(payload.get("agency_id")),
        normalise(payload.get("physical_address")),
        normalise(payload.get("district")),
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import agency contacts and locations."
    )

    parser.add_argument(
        "--base-url",
        required=True,
        help="Backend URL, with or without /api/v1.",
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Create records. Without this flag, only perform a dry run.",
    )

    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue importing after an individual API error.",
    )

    args = parser.parse_args()

    if not DATA_FILE.exists():
        raise SystemExit(f"Dataset not found: {DATA_FILE}")

    dataset = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    api = ApiClient(args.base_url)

    agencies = api.get_all("agencies")
    existing_contacts = api.get_all(CONTACT_ENDPOINT)
    existing_locations = api.get_all(LOCATION_ENDPOINT)

    agency_by_name = {
        normalise(agency.get("name")): agency
        for agency in agencies
    }

    existing_contact_keys = {
        contact_key(record)
        for record in existing_contacts
    }

    existing_location_keys = {
        location_key(record)
        for record in existing_locations
    }

    candidate_contacts: dict[
        tuple[str, ...],
        dict[str, Any],
    ] = {}

    candidate_locations: dict[
        tuple[str, ...],
        dict[str, Any],
    ] = {}

    agencies_found = set()
    agencies_missing = set()
    skipped = 0

    for service in dataset.get("services", []):
        agency_name = str(
            service.get("agency_name")
            or service.get("agency")
            or ""
        ).strip()

        agency = agency_by_name.get(normalise(agency_name))

        if not agency:
            agencies_missing.add(agency_name)
            continue

        agency_id = int(agency["id"])
        agencies_found.add(agency_id)

        for source in service.get("contacts", []):
            payload = build_contact_payload(
                agency_id,
                source,
                agency_name,
            )

            if payload is None:
                skipped += 1
                continue

            candidate_contacts[contact_key(payload)] = payload

        for source in service.get("locations", []):
            payload = build_location_payload(
                agency_id,
                source,
                agency_name,
            )

            if payload is None:
                print(
                    "  [location:skipped] "
                    f"{agency_name} | "
                    f"{source.get('name')} | "
                    "not a complete physical location"
                )
                skipped += 1
                continue

            candidate_locations[location_key(payload)] = payload

    mode = "APPLY" if args.apply else "DRY RUN"

    print(f"Backend: {api.base_url}")
    print(f"Mode: {mode}")
    print(f"Backend agencies: {len(agencies)}")
    print(f"Candidate contacts: {len(candidate_contacts)}")
    print(f"Candidate locations: {len(candidate_locations)}")
    print()

    stats = {
        "would_create": 0,
        "created": 0,
        "unchanged": 0,
        "failed": 0,
        "skipped": skipped,
    }

    for payload in candidate_contacts.values():
        key = contact_key(payload)

        if key in existing_contact_keys:
            stats["unchanged"] += 1
            print(f"[contacts:unchanged] {payload}")
            continue

        if not args.apply:
            stats["would_create"] += 1
            print(f"[contacts:would-create] {payload}")
            continue

        try:
            api.post(CONTACT_ENDPOINT, payload)
            existing_contact_keys.add(key)
            stats["created"] += 1
            print(f"[contacts:created] {payload}")
            time.sleep(0.05)

        except Exception as exc:
            stats["failed"] += 1
            print(f"[contacts:failed] {exc}")

            if not args.continue_on_error:
                raise

    for payload in candidate_locations.values():
        key = location_key(payload)

        if key in existing_location_keys:
            stats["unchanged"] += 1
            print(f"[locations:unchanged] {payload}")
            continue

        if not args.apply:
            stats["would_create"] += 1
            print(f"[locations:would-create] {payload}")
            continue

        try:
            api.post(LOCATION_ENDPOINT, payload)
            existing_location_keys.add(key)
            stats["created"] += 1
            print(f"[locations:created] {payload}")
            time.sleep(0.05)

        except Exception as exc:
            stats["failed"] += 1
            print(f"[locations:failed] {exc}")

            if not args.continue_on_error:
                raise

    print()
    print("Agency contact/location import summary")
    print(f"agencies_found={len(agencies_found)}")
    print(f"agencies_missing={len(agencies_missing)}")
    print(f"would_create={stats['would_create']}")
    print(f"created={stats['created']}")
    print(f"unchanged={stats['unchanged']}")
    print(f"skipped={stats['skipped']}")
    print(f"failed={stats['failed']}")

    if agencies_missing:
        print()
        print("Missing agencies:")

        for name in sorted(agencies_missing):
            print(f" - {name}")

    if not args.apply:
        print("Dry run complete. No records were changed.")

    return 1 if stats["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
