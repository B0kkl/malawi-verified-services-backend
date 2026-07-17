from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.agency import Agency
from app.repositories.agency_repository import AgencyRepository
from app.schemas.agency import AgencyCreate, AgencyUpdate


class AgencyService:
    @staticmethod
    def create_agency(
        db: Session,
        agency_data: AgencyCreate,
    ) -> Agency:
        existing_agency = AgencyRepository.get_by_name(
            db=db,
            name=agency_data.name,
        )

        if existing_agency:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An agency with this name already exists.",
            )

        return AgencyRepository.create(
            db=db,
            agency_data=agency_data,
        )

    @staticmethod
    def get_agency(
        db: Session,
        agency_id: int,
    ) -> Agency:
        agency = AgencyRepository.get_by_id(
            db=db,
            agency_id=agency_id,
        )

        if agency is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agency not found.",
            )

        return agency

    @staticmethod
    def get_agencies(
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Agency]:
        return AgencyRepository.get_all(
            db=db,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def update_agency(
        db: Session,
        agency_id: int,
        agency_data: AgencyUpdate,
    ) -> Agency:
        agency = AgencyService.get_agency(
            db=db,
            agency_id=agency_id,
        )

        if agency_data.name is not None:
            existing_agency = AgencyRepository.get_by_name(
                db=db,
                name=agency_data.name,
            )

            if (
                existing_agency is not None
                and existing_agency.id != agency_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An agency with this name already exists.",
                )

        return AgencyRepository.update(
            db=db,
            agency=agency,
            agency_data=agency_data,
        )

    @staticmethod
    def delete_agency(
        db: Session,
        agency_id: int,
    ) -> None:
        agency = AgencyService.get_agency(
            db=db,
            agency_id=agency_id,
        )

        AgencyRepository.delete(
            db=db,
            agency=agency,
        )