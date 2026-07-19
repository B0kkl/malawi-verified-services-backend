from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.requirement import Requirement
from app.schemas.requirement import RequirementCreate, RequirementUpdate


class RequirementRepository:
    @staticmethod
    def create(
        db: Session,
        requirement_data: RequirementCreate,
    ) -> Requirement:
        requirement = Requirement(
            **requirement_data.model_dump()
        )

        db.add(requirement)
        db.commit()
        db.refresh(requirement)

        return requirement

    @staticmethod
    def get_by_id(
        db: Session,
        requirement_id: int,
    ) -> Requirement | None:
        statement = select(Requirement).where(
            Requirement.id == requirement_id
        )

        return db.scalar(statement)

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Requirement]:
        statement = (
            select(Requirement)
            .order_by(Requirement.name.asc())
            .offset(skip)
            .limit(limit)
        )

        return list(db.scalars(statement).all())

    @staticmethod
    def get_by_service(
        db: Session,
        service_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Requirement]:
        statement = (
            select(Requirement)
            .where(Requirement.service_id == service_id)
            .order_by(
                Requirement.is_mandatory.desc(),
                Requirement.name.asc(),
            )
            .offset(skip)
            .limit(limit)
        )

        return list(db.scalars(statement).all())

    @staticmethod
    def update(
        db: Session,
        requirement: Requirement,
        requirement_data: RequirementUpdate,
    ) -> Requirement:
        update_data = requirement_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(requirement, field, value)

        db.commit()
        db.refresh(requirement)

        return requirement

    @staticmethod
    def delete(
        db: Session,
        requirement: Requirement,
    ) -> None:
        db.delete(requirement)
        db.commit()
