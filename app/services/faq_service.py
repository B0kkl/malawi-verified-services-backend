from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.faq import FAQ
from app.repositories.faq_repository import FAQRepository
from app.repositories.service_repository import ServiceRepository
from app.schemas.faq import FAQCreate, FAQUpdate


class FAQService:
    @staticmethod
    def create_faq(
        db: Session,
        faq_data: FAQCreate,
    ) -> FAQ:
        service_repository = ServiceRepository(db)

        service = service_repository.get_by_id(
            faq_data.service_id
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        return FAQRepository.create(
            db,
            faq_data,
        )

    @staticmethod
    def get_faq(
        db: Session,
        faq_id: int,
    ) -> FAQ:
        faq = FAQRepository.get_by_id(
            db,
            faq_id,
        )

        if faq is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FAQ not found.",
            )

        return faq

    @staticmethod
    def get_faqs(
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[FAQ]:
        return FAQRepository.get_all(
            db,
            skip,
            limit,
        )

    @staticmethod
    def get_service_faqs(
        db: Session,
        service_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[FAQ]:
        service_repository = ServiceRepository(db)

        service = service_repository.get_by_id(
            service_id
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        return FAQRepository.get_by_service(
            db,
            service_id,
            skip,
            limit,
        )

    @staticmethod
    def update_faq(
        db: Session,
        faq_id: int,
        faq_data: FAQUpdate,
    ) -> FAQ:
        faq = FAQService.get_faq(
            db,
            faq_id,
        )

        if faq_data.service_id is not None:
            service_repository = ServiceRepository(db)

            service = service_repository.get_by_id(
                faq_data.service_id
            )

            if service is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Service not found.",
                )

        return FAQRepository.update(
            db,
            faq,
            faq_data,
        )

    @staticmethod
    def delete_faq(
        db: Session,
        faq_id: int,
    ) -> None:
        faq = FAQService.get_faq(
            db,
            faq_id,
        )

        FAQRepository.delete(
            db,
            faq,
        )
