from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.faq import FAQ
from app.schemas.faq import FAQCreate, FAQUpdate


class FAQRepository:
    @staticmethod
    def create(
        db: Session,
        faq_data: FAQCreate,
    ) -> FAQ:
        faq = FAQ(
            **faq_data.model_dump()
        )

        db.add(faq)
        db.commit()
        db.refresh(faq)

        return faq

    @staticmethod
    def get_by_id(
        db: Session,
        faq_id: int,
    ) -> FAQ | None:
        statement = select(FAQ).where(
            FAQ.id == faq_id
        )

        return db.scalar(statement)

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[FAQ]:
        statement = (
            select(FAQ)
            .order_by(FAQ.id.asc())
            .offset(skip)
            .limit(limit)
        )

        return list(
            db.scalars(statement).all()
        )

    @staticmethod
    def get_by_service(
        db: Session,
        service_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[FAQ]:
        statement = (
            select(FAQ)
            .where(FAQ.service_id == service_id)
            .order_by(FAQ.id.asc())
            .offset(skip)
            .limit(limit)
        )

        return list(
            db.scalars(statement).all()
        )

    @staticmethod
    def update(
        db: Session,
        faq: FAQ,
        faq_data: FAQUpdate,
    ) -> FAQ:
        update_data = faq_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(faq, field, value)

        db.commit()
        db.refresh(faq)

        return faq

    @staticmethod
    def delete(
        db: Session,
        faq: FAQ,
    ) -> None:
        db.delete(faq)
        db.commit()
