from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate


class ContactRepository:
    @staticmethod
    def create(
        db: Session,
        contact_data: ContactCreate,
    ) -> Contact:
        contact = Contact(**contact_data.model_dump())

        db.add(contact)
        db.commit()
        db.refresh(contact)

        return contact

    @staticmethod
    def get_by_id(
        db: Session,
        contact_id: int,
    ) -> Contact | None:
        statement = select(Contact).where(
            Contact.id == contact_id
        )

        return db.scalar(statement)

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Contact]:
        statement = (
            select(Contact)
            .order_by(Contact.full_name.asc())
            .offset(skip)
            .limit(limit)
        )

        return list(db.scalars(statement).all())

    @staticmethod
    def get_by_agency(
        db: Session,
        agency_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Contact]:
        statement = (
            select(Contact)
            .where(Contact.agency_id == agency_id)
            .order_by(
                Contact.is_primary.desc(),
                Contact.full_name.asc(),
            )
            .offset(skip)
            .limit(limit)
        )

        return list(db.scalars(statement).all())

    @staticmethod
    def update(
        db: Session,
        contact: Contact,
        contact_data: ContactUpdate,
    ) -> Contact:
        update_data = contact_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(contact, field, value)

        db.commit()
        db.refresh(contact)

        return contact

    @staticmethod
    def delete(
        db: Session,
        contact: Contact,
    ) -> None:
        db.delete(contact)
        db.commit()

    @staticmethod
    def clear_primary_contacts(
        db: Session,
        agency_id: int,
        exclude_contact_id: int | None = None,
    ) -> None:
        statement = select(Contact).where(
            Contact.agency_id == agency_id,
            Contact.is_primary.is_(True),
        )

        contacts = list(db.scalars(statement).all())

        for contact in contacts:
            if (
                exclude_contact_id is None
                or contact.id != exclude_contact_id
            ):
                contact.is_primary = False

        db.flush()