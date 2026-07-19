from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.service import (
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
)
from app.services.service_service import ServiceService

router = APIRouter(
    prefix="/services",
    tags=["Services"],
)


@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
) -> ServiceResponse:
    service_service = ServiceService(db)
    return service_service.create_service(service_data)


@router.get(
    "",
    response_model=list[ServiceResponse],
)
def get_services(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[ServiceResponse]:
    service_service = ServiceService(db)

    return service_service.get_services(
        skip=skip,
        limit=limit,
    )


@router.get(
    "/agency/{agency_id}",
    response_model=list[ServiceResponse],
)
def get_agency_services(
    agency_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[ServiceResponse]:
    service_service = ServiceService(db)

    return service_service.get_agency_services(
        agency_id=agency_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
)
def get_service(
    service_id: int,
    db: Session = Depends(get_db),
) -> ServiceResponse:
    service_service = ServiceService(db)
    return service_service.get_service(service_id)


@router.patch(
    "/{service_id}",
    response_model=ServiceResponse,
)
def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    db: Session = Depends(get_db),
) -> ServiceResponse:
    service_service = ServiceService(db)

    return service_service.update_service(
        service_id=service_id,
        service_data=service_data,
    )


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
) -> Response:
    service_service = ServiceService(db)
    service_service.delete_service(service_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)