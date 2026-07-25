from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agency import Agency
from app.models.service import Service
from app.repositories.service_repository import ServiceRepository
from app.schemas.service import ServiceDetailsResponse


class PublicDirectoryService:
    def __init__(self, db: Session):
        self.db = db
        self.service_repository = ServiceRepository(db)

    def get_agencies(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Agency]:
        statement = (
            select(Agency)
            .where(Agency.is_active.is_(True))
            .order_by(Agency.name.asc())
            .offset(skip)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())

    def get_agency(
        self,
        agency_id: int,
    ) -> Agency:
        statement = select(Agency).where(
            Agency.id == agency_id,
            Agency.is_active.is_(True),
        )

        agency = self.db.scalar(statement)

        if agency is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active agency not found.",
            )

        return agency

    def get_services(
        self,
        search: str | None = None,
        category: str | None = None,
        agency_id: int | None = None,
        district: str | None = None,
        online_available: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Service]:
        if agency_id is not None:
            self.get_agency(agency_id)

        services = self.service_repository.search(
            search=search,
            category=category,
            agency_id=agency_id,
            district=district,
            online_available=online_available,
            is_active=True,
            skip=skip,
            limit=limit,
        )

        return [
            service
            for service in services
            if service.agency is not None
            and service.agency.is_active
        ]

    def get_service_details(
        self,
        service_id: int,
    ) -> ServiceDetailsResponse:
        service = self.service_repository.get_details(
            service_id
        )

        if (
            service is None
            or not service.is_active
            or service.agency is None
            or not service.agency.is_active
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active service not found.",
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