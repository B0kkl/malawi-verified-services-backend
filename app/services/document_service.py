from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.repositories.service_repository import ServiceRepository
from app.schemas.document import DocumentCreate, DocumentUpdate


class DocumentService:
    @staticmethod
    def create_document(
        db: Session,
        document_data: DocumentCreate,
    ) -> Document:
        service_repository = ServiceRepository(db)

        service = service_repository.get_by_id(
            document_data.service_id
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        return DocumentRepository.create(
            db,
            document_data,
        )

    @staticmethod
    def get_document(
        db: Session,
        document_id: int,
    ) -> Document:
        document = DocumentRepository.get_by_id(
            db,
            document_id,
        )

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )

        return document

    @staticmethod
    def get_documents(
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Document]:
        return DocumentRepository.get_all(
            db,
            skip,
            limit,
        )

    @staticmethod
    def get_service_documents(
        db: Session,
        service_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Document]:
        service_repository = ServiceRepository(db)

        service = service_repository.get_by_id(
            service_id
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        return DocumentRepository.get_by_service(
            db,
            service_id,
            skip,
            limit,
        )

    @staticmethod
    def update_document(
        db: Session,
        document_id: int,
        document_data: DocumentUpdate,
    ) -> Document:
        document = DocumentService.get_document(
            db,
            document_id,
        )

        if document_data.service_id is not None:
            service_repository = ServiceRepository(db)

            service = service_repository.get_by_id(
                document_data.service_id
            )

            if service is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Service not found.",
                )

        return DocumentRepository.update(
            db,
            document,
            document_data,
        )

    @staticmethod
    def delete_document(
        db: Session,
        document_id: int,
    ) -> None:
        document = DocumentService.get_document(
            db,
            document_id,
        )

        DocumentRepository.delete(
            db,
            document,
        )
