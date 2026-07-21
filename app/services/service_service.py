from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.service import Service
from app.repositories.agency_repository import AgencyRepository
from app.repositories.service_repository import ServiceRepository
from app.schemas.service import (
    ServiceCreate,
    ServiceDetailsResponse,
    ServiceUpdate,
)


class ServiceService:
    def __init__(self, db: Session):
        self.db = db
        self.service_repository = ServiceRepository(db)

    def validate_agency(self, agency_id: int) -> None:
        agency = AgencyRepository.get_by_id(
            self.db,
            agency_id,
        )

        if agency is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agency not found.",
            )

    def create_service(
        self,
        service_data: ServiceCreate,
    ) -> Service:
        self.validate_agency(service_data.agency_id)

        existing_service = (
            self.service_repository.get_by_name_and_agency(
                name=service_data.name,
                agency_id=service_data.agency_id,
            )
        )

        if existing_service is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This agency already has a service with this name.",
            )

        return self.service_repository.create(
            service_data
        )

    def get_service(
        self,
        service_id: int,
    ) -> Service:
        service = self.service_repository.get_by_id(
            service_id
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        return service

    def get_service_details(
        self,
        service_id: int,
    ) -> ServiceDetailsResponse:
        service = self.service_repository.get_details(
            service_id
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        details = ServiceDetailsResponse.model_validate(
            service
        )

        return details.model_copy(
            update={
                "contacts": service.agency.contacts,
                "locations": service.agency.locations,
            }
        )

    def get_services(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Service]:
        return self.service_repository.get_all(
            skip=skip,
            limit=limit,
        )

    def search_services(
        self,
        search: str | None = None,
        category: str | None = None,
        agency_id: int | None = None,
        district: str | None = None,
        online_available: bool | None = None,
        is_active: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Service]:
        if agency_id is not None:
            self.validate_agency(agency_id)

        return self.service_repository.search(
            search=search,
            category=category,
            agency_id=agency_id,
            district=district,
            online_available=online_available,
            is_active=is_active,
            skip=skip,
            limit=limit,
        )

    def get_agency_services(
        self,
        agency_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Service]:
        self.validate_agency(agency_id)

        return self.service_repository.get_by_agency(
            agency_id=agency_id,
            skip=skip,
            limit=limit,
        )

    def update_service(
        self,
        service_id: int,
        service_data: ServiceUpdate,
    ) -> Service:
        service = self.get_service(service_id)

        if (
            service_data.agency_id is not None
            and service_data.agency_id != service.agency_id
        ):
            self.validate_agency(
                service_data.agency_id
            )

        target_agency_id = (
            service_data.agency_id
            if service_data.agency_id is not None
            else service.agency_id
        )

        target_name = (
            service_data.name
            if service_data.name is not None
            else service.name
        )

        duplicate = (
            self.service_repository.get_by_name_and_agency(
                name=target_name,
                agency_id=target_agency_id,
            )
        )

        if (
            duplicate is not None
            and duplicate.id != service.id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This agency already has a service with this name.",
            )

        return self.service_repository.update(
            service=service,
            service_data=service_data,
        )

    def delete_service(
        self,
        service_id: int,
    ) -> None:
        service = self.get_service(service_id)

        self.service_repository.delete(
            service
        )
