from __future__ import annotations

from typing import Any

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.agency import Agency
from app.models.contact import Contact
from app.models.document import Document
from app.models.faq import FAQ
from app.models.fee import Fee
from app.models.location import Location
from app.models.requirement import Requirement
from app.models.service import Service


def supported_values(
    model: type,
    values: dict[str, Any],
) -> dict[str, Any]:
    """Return only values supported by the model's database table."""
    column_names = {
        column.key
        for column in inspect(model).mapper.column_attrs
    }

    return {
        key: value
        for key, value in values.items()
        if key in column_names
    }


def get_or_create(
    db: Session,
    model: type,
    lookup: dict[str, Any],
    defaults: dict[str, Any] | None = None,
):
    valid_lookup = supported_values(model, lookup)

    if not valid_lookup:
        raise ValueError(
            f"No valid lookup fields supplied for {model.__name__}."
        )

    instance = (
        db.query(model)
        .filter_by(**valid_lookup)
        .first()
    )

    if instance is not None:
        return instance, False

    create_values = {
        **valid_lookup,
        **supported_values(model, defaults or {}),
    }

    instance = model(**create_values)
    db.add(instance)
    db.flush()

    return instance, True


def seed_agency(
    db: Session,
    data: dict[str, Any],
) -> tuple[Agency, bool]:
    agency, created = get_or_create(
        db=db,
        model=Agency,
        lookup={
            "name": data["name"],
        },
        defaults={
            "short_name": data["short_name"],
            "category": "Government Agency",
            "country": "Malawi",
            "city": data["city"],
            "address": data["address"],
            "website": data["website"],
            "description": data["description"],
            "is_active": True,
        },
    )

    return agency, created


def seed_contact(
    db: Session,
    agency_id: int,
    data: dict[str, Any],
) -> bool:
    _, created = get_or_create(
        db=db,
        model=Contact,
        lookup={
            "agency_id": agency_id,
            "email": data["email"],
        },
        defaults={
            "full_name": data["name"],
            "job_title": "Customer Service Representative",
            "department": data["department"],
            "phone_number": data["phone"],
            "alternative_phone": None,
            "email": data["email"],
            "office_hours": (
                "Monday to Friday, 08:00 to 17:00"
            ),
            "notes": (
                "Prototype contact information. "
                "Verify before production use."
            ),
            "is_primary": True,
            "is_active": True,
        },
    )

    return created


def seed_location(
    db: Session,
    agency_id: int,
    data: dict[str, Any],
) -> bool:
    _, created = get_or_create(
        db=db,
        model=Location,
        lookup={
            "agency_id": agency_id,
            "district": data["district"],
            "physical_address": data["address"],
        },
        defaults={
            "physical_address": data["address"],
            "postal_address": data.get("postal_address"),
            "phone_number": data.get("phone"),
            "email": data.get("email"),
            "is_head_office": data.get(
                "is_head_office",
                True,
            ),
        },
    )

    return created


def seed_service(
    db: Session,
    agency_id: int,
    data: dict[str, Any],
) -> tuple[Service, bool]:
    service, created = get_or_create(
        db=db,
        model=Service,
        lookup={
            "agency_id": agency_id,
            "name": data["name"],
        },
        defaults={
            "category": data["category"],
            "description": data["description"],
            "requirements": data.get(
                "requirements_summary"
            ),
            "application_process": data.get(
                "application_process"
            ),
            "processing_time": data.get(
                "processing_time"
            ),
            "fee_amount": data.get(
                "fee_amount",
                "0.00",
            ),
            "fee_currency": "MWK",
            "office_location": data.get(
                "office_location"
            ),
            "online_available": data.get(
                "online_available",
                False,
            ),
            "online_url": data.get("online_url"),
            "contact_phone": data.get(
                "contact_phone"
            ),
            "contact_email": data.get(
                "contact_email"
            ),
            "is_active": True,
        },
    )

    return service, created


def seed_requirement(
    db: Session,
    service_id: int,
    data: dict[str, Any],
) -> bool:
    _, created = get_or_create(
        db=db,
        model=Requirement,
        lookup={
            "service_id": service_id,
            "name": data["name"],
        },
        defaults={
            "description": data["description"],
            "is_mandatory": data.get(
                "is_mandatory",
                True,
            ),
        },
    )

    return created


def seed_fee(
    db: Session,
    service_id: int,
    data: dict[str, Any],
) -> bool:
    lookup = {
        "service_id": service_id,
        "name": data["name"],
        "fee_type": data["name"],
    }

    valid_lookup = supported_values(Fee, lookup)

    # Use one descriptive field plus service_id.
    if "name" in valid_lookup:
        valid_lookup.pop("fee_type", None)
    elif "fee_type" in valid_lookup:
        valid_lookup.pop("name", None)

    _, created = get_or_create(
        db=db,
        model=Fee,
        lookup=valid_lookup,
        defaults={
            "name": data["name"],
            "fee_type": data["name"],
            "description": data["description"],
            "amount": data.get("amount", "0.00"),
            "fee_amount": data.get(
                "amount",
                "0.00",
            ),
            "currency": "MWK",
            "fee_currency": "MWK",
            "is_mandatory": data.get(
                "is_mandatory",
                True,
            ),
        },
    )

    return created


def seed_faq(
    db: Session,
    service_id: int,
    data: dict[str, str],
) -> bool:
    _, created = get_or_create(
        db=db,
        model=FAQ,
        lookup={
            "service_id": service_id,
            "question": data["question"],
        },
        defaults={
            "answer": data["answer"],
        },
    )

    return created


def seed_document(
    db: Session,
    service_id: int,
    data: dict[str, Any],
) -> bool:
    _, created = get_or_create(
        db=db,
        model=Document,
        lookup={
            "service_id": service_id,
            "title": data["title"],
        },
        defaults={
            "description": data["description"],
            "document_type": data["document_type"],
            "file_url": data["file_url"],
            "is_downloadable": data.get(
                "is_downloadable",
                False,
            ),
        },
    )

    return created


AGENCIES = [
    {
        "name": "Malawi Revenue Authority",
        "short_name": "MRA",
        "city": "Blantyre",
        "address": (
            "Msonkho House, Independence Drive, Blantyre"
        ),
        "website": "https://www.mra.mw",
        "description": (
            "Government authority responsible for tax and "
            "customs administration in Malawi."
        ),
        "contact": {
            "name": "MRA General Enquiries",
            "department": "Customer Service",
            "phone": "+265 1 822 588",
            "email": "callcentre@mra.mw",
        },
        "location": {
            "name": "MRA Head Office",
            "district": "Blantyre",
            "region": "Southern Region",
            "address": (
                "Msonkho House, Independence Drive, Blantyre"
            ),
            "phone": "+265 1 822 588",
            "is_head_office": True,
        },
        "services": [
            {
                "name": "Taxpayer Identification Number Registration",
                "category": "Taxation",
                "description": (
                    "Registration of individuals and organisations "
                    "for a taxpayer identification number."
                ),
                "requirements_summary": (
                    "Identification and supporting registration "
                    "documents are required."
                ),
                "application_process": (
                    "Submit the required information to MRA through "
                    "the available registration channel."
                ),
                "processing_time": (
                    "Processing time depends on verification."
                ),
                "online_available": True,
                "online_url": "https://www.mra.mw",
                "contact_email": "callcentre@mra.mw",
                "requirements": [
                    {
                        "name": "National ID or Passport",
                        "description": (
                            "A valid identification document for "
                            "the applicant."
                        ),
                    },
                    {
                        "name": "Business Registration Documents",
                        "description": (
                            "Required where the applicant is a "
                            "registered business or organisation."
                        ),
                    },
                ],
                "fees": [
                    {
                        "name": "Registration Fee",
                        "description": (
                            "Confirm the current applicable fee "
                            "directly with MRA."
                        ),
                        "amount": "0.00",
                    }
                ],
                "faqs": [
                    {
                        "question": "Who needs a taxpayer number?",
                        "answer": (
                            "Individuals and organisations with tax "
                            "obligations may be required to register."
                        ),
                    },
                    {
                        "question": "Can registration be started online?",
                        "answer": (
                            "Online services may be available through "
                            "MRA's official platforms."
                        ),
                    },
                ],
                "documents": [
                    {
                        "title": "Taxpayer Registration Guidance",
                        "description": (
                            "Official information and registration "
                            "guidance."
                        ),
                        "document_type": "Guidance",
                        "file_url": "https://www.mra.mw",
                        "is_downloadable": False,
                    }
                ],
            },
            {
                "name": "Tax Clearance Certificate",
                "category": "Taxation",
                "description": (
                    "Application for evidence that a taxpayer's "
                    "tax affairs meet the applicable requirements."
                ),
                "application_process": (
                    "Submit an application and allow MRA to verify "
                    "the taxpayer's compliance status."
                ),
                "processing_time": (
                    "Depends on compliance verification."
                ),
                "online_available": True,
                "online_url": "https://www.mra.mw",
                "contact_email": "callcentre@mra.mw",
                "requirements": [
                    {
                        "name": "Taxpayer Identification Number",
                        "description": (
                            "A valid taxpayer identification number."
                        ),
                    },
                    {
                        "name": "Up-to-date Tax Records",
                        "description": (
                            "Relevant tax returns and payment records "
                            "must be available for verification."
                        ),
                    },
                ],
                "fees": [],
                "faqs": [
                    {
                        "question": (
                            "Why can a clearance application be delayed?"
                        ),
                        "answer": (
                            "Outstanding returns, payments or incomplete "
                            "records may require resolution."
                        ),
                    }
                ],
                "documents": [],
            },
        ],
    },
    {
        "name": (
            "Department of Immigration and Citizenship Services"
        ),
        "short_name": "DICS",
        "city": "Blantyre",
        "address": "Immigration Headquarters, Blantyre",
        "website": "https://www.immigration.gov.mw",
        "description": (
            "Government department responsible for immigration, "
            "passports, permits and citizenship services."
        ),
        "contact": {
            "name": "Immigration General Enquiries",
            "department": "Customer Service",
            "phone": "+265 1 823 777",
            "email": "info@immigration.gov.mw",
        },
        "location": {
            "name": "Immigration Headquarters",
            "district": "Blantyre",
            "region": "Southern Region",
            "address": "Immigration Headquarters, Blantyre",
            "phone": "+265 1 823 777",
            "is_head_office": True,
        },
        "services": [
            {
                "name": "Malawi Passport Application",
                "category": "Immigration",
                "description": (
                    "Application for a new Malawi passport."
                ),
                "application_process": (
                    "Complete the application process, submit the "
                    "required documents and complete identity checks."
                ),
                "processing_time": (
                    "Processing time depends on the application type "
                    "and verification."
                ),
                "online_available": True,
                "online_url": (
                    "https://www.immigration.gov.mw"
                ),
                "contact_email": "info@immigration.gov.mw",
                "requirements": [
                    {
                        "name": "National ID",
                        "description": (
                            "Original or acceptable copy of a valid "
                            "Malawi National ID."
                        ),
                    },
                    {
                        "name": "Birth Certificate",
                        "description": (
                            "Birth registration evidence may be "
                            "required."
                        ),
                    },
                    {
                        "name": "Passport Photographs",
                        "description": (
                            "Photographs meeting the current passport "
                            "specifications."
                        ),
                    },
                ],
                "fees": [
                    {
                        "name": "Passport Application Fee",
                        "description": (
                            "Fees vary by passport type and processing "
                            "option. Confirm the current official fee."
                        ),
                        "amount": "0.00",
                    }
                ],
                "faqs": [
                    {
                        "question": (
                            "How can I check passport requirements?"
                        ),
                        "answer": (
                            "Confirm the latest requirements through "
                            "the Immigration Department's official "
                            "channels before applying."
                        ),
                    }
                ],
                "documents": [
                    {
                        "title": "Passport Application Information",
                        "description": (
                            "Passport application guidance and official "
                            "service information."
                        ),
                        "document_type": "Application Guidance",
                        "file_url": (
                            "https://www.immigration.gov.mw"
                        ),
                        "is_downloadable": False,
                    }
                ],
            },
            {
                "name": "Malawi Passport Renewal",
                "category": "Immigration",
                "description": (
                    "Renewal or replacement of an existing Malawi "
                    "passport."
                ),
                "application_process": (
                    "Provide the existing passport and the required "
                    "identity and application documents."
                ),
                "processing_time": (
                    "Depends on verification and processing option."
                ),
                "online_available": True,
                "online_url": (
                    "https://www.immigration.gov.mw"
                ),
                "requirements": [
                    {
                        "name": "Existing Passport",
                        "description": (
                            "The current or expired passport should be "
                            "presented where available."
                        ),
                    },
                    {
                        "name": "National ID",
                        "description": (
                            "A valid Malawi National ID."
                        ),
                    },
                ],
                "fees": [
                    {
                        "name": "Passport Renewal Fee",
                        "description": (
                            "Confirm the latest renewal fee directly "
                            "with Immigration."
                        ),
                        "amount": "0.00",
                    }
                ],
                "faqs": [],
                "documents": [],
            },
        ],
    },
    {
        "name": (
            "Directorate of Road Traffic and Safety Services"
        ),
        "short_name": "DRTSS",
        "city": "Lilongwe",
        "address": "Road Traffic Headquarters, Lilongwe",
        "website": "https://www.drtss.gov.mw",
        "description": (
            "Government directorate responsible for driver licensing, "
            "vehicle registration and road safety services."
        ),
        "contact": {
            "name": "Road Traffic General Enquiries",
            "department": "Customer Service",
            "phone": "+265 1 756 400",
            "email": "info@drtss.gov.mw",
        },
        "location": {
            "name": "Road Traffic Headquarters",
            "district": "Lilongwe",
            "region": "Central Region",
            "address": "Road Traffic Headquarters, Lilongwe",
            "phone": "+265 1 756 400",
            "is_head_office": True,
        },
        "services": [
            {
                "name": "Driver's Licence Renewal",
                "category": "Transport",
                "description": (
                    "Renewal of an existing Malawi driver's licence."
                ),
                "application_process": (
                    "Present the required identification, existing "
                    "licence and supporting documents."
                ),
                "processing_time": (
                    "Depends on verification and service availability."
                ),
                "online_available": True,
                "online_url": "https://www.drtss.gov.mw",
                "requirements": [
                    {
                        "name": "Existing Driver's Licence",
                        "description": (
                            "The existing or expired driver's licence."
                        ),
                    },
                    {
                        "name": "National ID",
                        "description": (
                            "A valid national identification document."
                        ),
                    },
                ],
                "fees": [
                    {
                        "name": "Licence Renewal Fee",
                        "description": (
                            "Confirm the current fee through official "
                            "Road Traffic channels."
                        ),
                        "amount": "0.00",
                    }
                ],
                "faqs": [
                    {
                        "question": (
                            "Can an expired driver's licence be renewed?"
                        ),
                        "answer": (
                            "Renewal may be possible subject to the "
                            "current Road Traffic requirements."
                        ),
                    }
                ],
                "documents": [],
            },
            {
                "name": "Motor Vehicle Registration",
                "category": "Transport",
                "description": (
                    "Registration of a motor vehicle in Malawi."
                ),
                "application_process": (
                    "Submit ownership, identity and vehicle documents "
                    "for inspection and verification."
                ),
                "processing_time": (
                    "Depends on document and vehicle verification."
                ),
                "online_available": True,
                "online_url": "https://www.drtss.gov.mw",
                "requirements": [
                    {
                        "name": "Proof of Ownership",
                        "description": (
                            "Valid documentation showing ownership of "
                            "the vehicle."
                        ),
                    },
                    {
                        "name": "Vehicle Inspection Documentation",
                        "description": (
                            "Inspection or roadworthiness documentation "
                            "where required."
                        ),
                    },
                ],
                "fees": [
                    {
                        "name": "Vehicle Registration Fee",
                        "description": (
                            "The fee depends on the applicable vehicle "
                            "registration rules."
                        ),
                        "amount": "0.00",
                    }
                ],
                "faqs": [],
                "documents": [],
            },
        ],
    },
    {
        "name": "National Registration Bureau",
        "short_name": "NRB",
        "city": "Lilongwe",
        "address": "National Registration Bureau, Lilongwe",
        "website": "https://www.nrb.gov.mw",
        "description": (
            "Government bureau responsible for national identification "
            "and civil registration services."
        ),
        "contact": {
            "name": "NRB General Enquiries",
            "department": "Customer Service",
            "phone": "+265 1 789 411",
            "email": "info@nrb.gov.mw",
        },
        "location": {
            "name": "NRB Headquarters",
            "district": "Lilongwe",
            "region": "Central Region",
            "address": "National Registration Bureau, Lilongwe",
            "phone": "+265 1 789 411",
            "is_head_office": True,
        },
        "services": [
            {
                "name": "National ID Registration",
                "category": "Civil Registration",
                "description": (
                    "Registration of eligible citizens for a Malawi "
                    "National Identification Card."
                ),
                "application_process": (
                    "Attend an authorised registration centre with "
                    "the required identity and supporting evidence."
                ),
                "processing_time": (
                    "Depends on registration and identity verification."
                ),
                "online_available": False,
                "requirements": [
                    {
                        "name": "Proof of Identity",
                        "description": (
                            "Acceptable identity or civil registration "
                            "evidence."
                        ),
                    },
                    {
                        "name": "Proof of Citizenship",
                        "description": (
                            "Supporting evidence may be required during "
                            "registration."
                        ),
                    },
                ],
                "fees": [
                    {
                        "name": "Initial Registration Fee",
                        "description": (
                            "Confirm whether any fee applies through "
                            "official NRB channels."
                        ),
                        "amount": "0.00",
                    }
                ],
                "faqs": [
                    {
                        "question": (
                            "Where can National ID registration be done?"
                        ),
                        "answer": (
                            "Registration is conducted at authorised "
                            "NRB registration centres."
                        ),
                    }
                ],
                "documents": [],
            },
            {
                "name": "National ID Replacement",
                "category": "Civil Registration",
                "description": (
                    "Replacement of a lost, damaged or unusable "
                    "National ID card."
                ),
                "application_process": (
                    "Report the issue and submit the required identity "
                    "and replacement documentation."
                ),
                "processing_time": (
                    "Depends on identity verification."
                ),
                "online_available": False,
                "requirements": [
                    {
                        "name": "Replacement Request",
                        "description": (
                            "A completed request explaining why the "
                            "National ID requires replacement."
                        ),
                    },
                    {
                        "name": "Supporting Identification",
                        "description": (
                            "Available identity or registration evidence."
                        ),
                    },
                ],
                "fees": [
                    {
                        "name": "Replacement Fee",
                        "description": (
                            "Confirm the latest replacement fee with "
                            "the National Registration Bureau."
                        ),
                        "amount": "0.00",
                    }
                ],
                "faqs": [],
                "documents": [],
            },
        ],
    },
    {
        "name": "Malawi Police Service",
        "short_name": "MPS",
        "city": "Lilongwe",
        "address": "Malawi Police Service Headquarters, Lilongwe",
        "website": "https://www.police.gov.mw",
        "description": (
            "National police service responsible for public safety, "
            "law enforcement and related public services."
        ),
        "contact": {
            "name": "Police General Enquiries",
            "department": "Public Relations",
            "phone": "+265 1 796 333",
            "email": "info@police.gov.mw",
        },
        "location": {
            "name": "Malawi Police Headquarters",
            "district": "Lilongwe",
            "region": "Central Region",
            "address": (
                "Malawi Police Service Headquarters, Lilongwe"
            ),
            "phone": "+265 1 796 333",
            "is_head_office": True,
        },
        "services": [
            {
                "name": "Police Clearance Certificate",
                "category": "Public Safety",
                "description": (
                    "Application for a police clearance or criminal "
                    "record certificate."
                ),
                "application_process": (
                    "Submit identification, fingerprints and the "
                    "required application information."
                ),
                "processing_time": (
                    "Depends on identity and record verification."
                ),
                "online_available": False,
                "requirements": [
                    {
                        "name": "National ID or Passport",
                        "description": (
                            "A valid identity document for the applicant."
                        ),
                    },
                    {
                        "name": "Fingerprint Record",
                        "description": (
                            "Fingerprints taken through an authorised "
                            "process."
                        ),
                    },
                    {
                        "name": "Passport Photographs",
                        "description": (
                            "Recent photographs where required."
                        ),
                    },
                ],
                "fees": [
                    {
                        "name": "Police Clearance Fee",
                        "description": (
                            "Confirm the current applicable fee with "
                            "the Malawi Police Service."
                        ),
                        "amount": "0.00",
                    }
                ],
                "faqs": [
                    {
                        "question": (
                            "Why is a police clearance certificate needed?"
                        ),
                        "answer": (
                            "It may be requested for employment, travel, "
                            "immigration or other official purposes."
                        ),
                    }
                ],
                "documents": [],
            }
        ],
    },
]


def seed_database() -> None:
    db = SessionLocal()

    counters = {
        "agencies": 0,
        "contacts": 0,
        "locations": 0,
        "services": 0,
        "requirements": 0,
        "fees": 0,
        "faqs": 0,
        "documents": 0,
    }

    try:
        for agency_data in AGENCIES:
            agency, created = seed_agency(
                db,
                agency_data,
            )
            counters["agencies"] += int(created)

            counters["contacts"] += int(
                seed_contact(
                    db,
                    agency.id,
                    agency_data["contact"],
                )
            )

            counters["locations"] += int(
                seed_location(
                    db,
                    agency.id,
                    agency_data["location"],
                )
            )

            for service_data in agency_data["services"]:
                service, created = seed_service(
                    db,
                    agency.id,
                    service_data,
                )
                counters["services"] += int(created)

                for requirement in service_data.get(
                    "requirements",
                    [],
                ):
                    counters["requirements"] += int(
                        seed_requirement(
                            db,
                            service.id,
                            requirement,
                        )
                    )

                for fee in service_data.get("fees", []):
                    counters["fees"] += int(
                        seed_fee(
                            db,
                            service.id,
                            fee,
                        )
                    )

                for faq in service_data.get("faqs", []):
                    counters["faqs"] += int(
                        seed_faq(
                            db,
                            service.id,
                            faq,
                        )
                    )

                for document in service_data.get(
                    "documents",
                    [],
                ):
                    counters["documents"] += int(
                        seed_document(
                            db,
                            service.id,
                            document,
                        )
                    )

        db.commit()

        print("Sample government data seeded successfully.")
        print("-------------------------------------------")

        for item, count in counters.items():
            print(f"New {item}: {count}")

        print()
        print(
            "Note: fees, contacts and processing details are "
            "prototype sample data and must be officially verified."
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()


