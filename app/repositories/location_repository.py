from sqlalchemy.orm import Session

from app.models.location import Location
from app.schemas.location import LocationCreate, LocationUpdate


class LocationRepository:
    @staticmethod
    def create(
        db: Session,
        location_data: LocationCreate,
    ) -> Location:
        location = Location(
            **location_data.model_dump()
        )

        db.add(location)
        db.commit()
        db.refresh(location)

        return location

    @staticmethod
    def get_by_id(
        db: Session,
        location_id: int,
    ) -> Location | None:
        return (
            db.query(Location)
            .filter(Location.id == location_id)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Location]:
        return (
            db.query(Location)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_agency(
        db: Session,
        agency_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Location]:
        return (
            db.query(Location)
            .filter(Location.agency_id == agency_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update(
        db: Session,
        location: Location,
        location_data: LocationUpdate,
    ) -> Location:
        update_data = location_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(location, field, value)

        db.commit()
        db.refresh(location)

        return location

    @staticmethod
    def delete(
        db: Session,
        location: Location,
    ) -> None:
        db.delete(location)
        db.commit()
