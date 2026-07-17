from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agency import Agency
from app.schemas.agency import AgencyCreate, AgencyUpdate


class AgencyRepository:
    @staticmethod
    def create(db: Session, agency_data: AgencyCreate) -> Agency:
        agency = Agency(**agency_data.model_dump())

        db.add(agency)
        db.commit()
        db.refresh(agency)

        return agency

    @staticmethod
    def get_by_id(db: Session, agency_id: int) -> Agency | None:
        statement = select(Agency).where(Agency.id == agency_id)
        return db.scalar(statement)

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Agency]:
        statement = (
            select(Agency)
            .order_by(Agency.name.asc())
            .offset(skip)
            .limit(limit)
        )

        return list(db.scalars(statement).all())

    @staticmethod
    def get_by_name(db: Session, name: str) -> Agency | None:
        statement = select(Agency).where(Agency.name == name)
        return db.scalar(statement)

    @staticmethod
    def update(
        db: Session,
        agency: Agency,
        agency_data: AgencyUpdate,
    ) -> Agency:
        update_data = agency_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(agency, field, value)

        db.commit()
        db.refresh(agency)

        return agency

    @staticmethod
    def delete(db: Session, agency: Agency) -> None:
        db.delete(agency)
        db.commit()