from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.location import Location
from app.repositories.agency_repository import AgencyRepository
from app.repositories.location_repository import LocationRepository
from app.schemas.location import LocationCreate, LocationUpdate


class LocationService:
    @staticmethod
    def create_location(
        db: Session,
        location_data: LocationCreate,
    ) -> Location:
        agency = AgencyRepository.get_by_id(
            db=db,
            agency_id=location_data.agency_id,
        )

        if agency is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agency not found.",
            )

        return LocationRepository.create(
            db=db,
            location_data=location_data,
        )

    @staticmethod
    def get_locations(
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Location]:
        return LocationRepository.get_all(
            db=db,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def get_location(
        db: Session,
        location_id: int,
    ) -> Location:
        location = LocationRepository.get_by_id(
            db=db,
            location_id=location_id,
        )

        if location is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found.",
            )

        return location

    @staticmethod
    def get_agency_locations(
        db: Session,
        agency_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Location]:
        agency = AgencyRepository.get_by_id(
            db=db,
            agency_id=agency_id,
        )

        if agency is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agency not found.",
            )

        return LocationRepository.get_by_agency(
            db=db,
            agency_id=agency_id,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def update_location(
        db: Session,
        location_id: int,
        location_data: LocationUpdate,
    ) -> Location:
        location = LocationService.get_location(
            db=db,
            location_id=location_id,
        )

        if location_data.agency_id is not None:
            agency = AgencyRepository.get_by_id(
                db=db,
                agency_id=location_data.agency_id,
            )

            if agency is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Agency not found.",
                )

        return LocationRepository.update(
            db=db,
            location=location,
            location_data=location_data,
        )

    @staticmethod
    def delete_location(
        db: Session,
        location_id: int,
    ) -> None:
        location = LocationService.get_location(
            db=db,
            location_id=location_id,
        )

        LocationRepository.delete(
            db=db,
            location=location,
        )
