from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.fee import Fee
from app.schemas.fee import FeeCreate, FeeUpdate


class FeeRepository:
    @staticmethod
    def create(
        db: Session,
        fee_data: FeeCreate,
    ) -> Fee:
        fee = Fee(
            **fee_data.model_dump()
        )

        db.add(fee)
        db.commit()
        db.refresh(fee)

        return fee

    @staticmethod
    def get_by_id(
        db: Session,
        fee_id: int,
    ) -> Fee | None:
        statement = select(Fee).where(
            Fee.id == fee_id
        )

        return db.scalar(statement)

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Fee]:
        statement = (
            select(Fee)
            .order_by(Fee.name.asc())
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
    ) -> list[Fee]:
        statement = (
            select(Fee)
            .where(Fee.service_id == service_id)
            .order_by(Fee.amount.asc())
            .offset(skip)
            .limit(limit)
        )

        return list(db.scalars(statement).all())

    @staticmethod
    def update(
        db: Session,
        fee: Fee,
        fee_data: FeeUpdate,
    ) -> Fee:
        update_data = fee_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(fee, field, value)

        db.commit()
        db.refresh(fee)

        return fee

    @staticmethod
    def delete(
        db: Session,
        fee: Fee,
    ) -> None:
        db.delete(fee)
        db.commit()
