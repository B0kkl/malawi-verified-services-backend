from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.repositories.agency_repository import AgencyRepository
from app.repositories.contact_repository import ContactRepository
from app.schemas.contact import ContactCreate, ContactUpdate


class ContactService:
    @staticmethod
    def validate_agency(
        db: Session,
        agency_id: int,
    ) -> None:
        agency = AgencyRepository.get_by_id(
            db=db,
            agency_id=agency_id,
        )

        if agency is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agency not found.",
            )

    @staticmethod
    def create_contact(
        db: Session,
        contact_data: ContactCreate,
    ) -> Contact:
        ContactService.validate_agency(
            db=db,
            agency_id=contact_data.agency_id,
        )

        if contact_data.is_primary:
            ContactRepository.clear_primary_contacts(
                db=db,
                agency_id=contact_data.agency_id,
            )

        return ContactRepository.create(
            db=db,
            contact_data=contact_data,
        )

    @staticmethod
    def get_contact(
        db: Session,
        contact_id: int,
    ) -> Contact:
        contact = ContactRepository.get_by_id(
            db=db,
            contact_id=contact_id,
        )

        if contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found.",
            )

        return contact

    @staticmethod
    def get_contacts(
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Contact]:
        return ContactRepository.get_all(
            db=db,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def get_agency_contacts(
        db: Session,
        agency_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Contact]:
        ContactService.validate_agency(
            db=db,
            agency_id=agency_id,
        )

        return ContactRepository.get_by_agency(
            db=db,
            agency_id=agency_id,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def update_contact(
        db: Session,
        contact_id: int,
        contact_data: ContactUpdate,
    ) -> Contact:
        contact = ContactService.get_contact(
            db=db,
            contact_id=contact_id,
        )

        target_agency_id = (
            contact_data.agency_id
            if contact_data.agency_id is not None
            else contact.agency_id
        )

        if contact_data.agency_id is not None:
            ContactService.validate_agency(
                db=db,
                agency_id=contact_data.agency_id,
            )

        if contact_data.is_primary is True:
            ContactRepository.clear_primary_contacts(
                db=db,
                agency_id=target_agency_id,
                exclude_contact_id=contact.id,
            )

        return ContactRepository.update(
            db=db,
            contact=contact,
            contact_data=contact_data,
        )

    @staticmethod
    def delete_contact(
        db: Session,
        contact_id: int,
    ) -> None:
        contact = ContactService.get_contact(
            db=db,
            contact_id=contact_id,
        )

        ContactRepository.delete(
            db=db,
            contact=contact,
        )