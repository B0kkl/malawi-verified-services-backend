from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.api_key import require_api_application
from app.database.session import get_db
from app.models.api_application import APIApplication
from app.schemas.agency import AgencyResponse
from app.schemas.service import (
    ServiceDetailsResponse,
    ServiceResponse,
)
from app.services.public_directory_service import (
    PublicDirectoryService,
)


router = APIRouter(
    prefix="/public",
    tags=["Public API"],
)


@router.get("/access-check")
def check_public_api_access(
    application: APIApplication = Depends(
        require_api_application
    ),
):
    return {
        "success": True,
        "message": "API access confirmed.",
        "application": {
            "id": application.id,
            "company_name": application.company_name,
            "api_key_prefix": application.api_key_prefix,
            "request_count": application.request_count,
        },
    }


@router.get(
    "/agencies",
    response_model=list[AgencyResponse],
)
def get_public_agencies(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
    _application: APIApplication = Depends(
        require_api_application
    ),
):
    public_service = PublicDirectoryService(db)

    return public_service.get_agencies(
        skip=skip,
        limit=limit,
    )


@router.get(
    "/agencies/{agency_id}",
    response_model=AgencyResponse,
)
def get_public_agency(
    agency_id: int,
    db: Session = Depends(get_db),
    _application: APIApplication = Depends(
        require_api_application
    ),
):
    public_service = PublicDirectoryService(db)

    return public_service.get_agency(
        agency_id=agency_id,
    )


@router.get(
    "/services",
    response_model=list[ServiceResponse],
)
def get_public_services(
    search: str | None = Query(
        default=None,
        min_length=1,
    ),
    category: str | None = Query(
        default=None,
        min_length=1,
    ),
    agency_id: int | None = Query(
        default=None,
        gt=0,
    ),
    district: str | None = Query(
        default=None,
        min_length=1,
    ),
    online_available: bool | None = Query(
        default=None,
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
    _application: APIApplication = Depends(
        require_api_application
    ),
):
    public_service = PublicDirectoryService(db)

    return public_service.get_services(
        search=search,
        category=category,
        agency_id=agency_id,
        district=district,
        online_available=online_available,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/services/{service_id}",
    response_model=ServiceDetailsResponse,
)
def get_public_service(
    service_id: int,
    db: Session = Depends(get_db),
    _application: APIApplication = Depends(
        require_api_application
    ),
):
    public_service = PublicDirectoryService(db)

    return public_service.get_service_details(
        service_id=service_id,
    )