from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate


class DocumentRepository:
    @staticmethod
    def create(
        db: Session,
        document_data: DocumentCreate,
    ) -> Document:
        document = Document(
            **document_data.model_dump(
                mode="json"
            )
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    @staticmethod
    def get_by_id(
        db: Session,
        document_id: int,
    ) -> Document | None:
        statement = select(Document).where(
            Document.id == document_id
        )

        return db.scalar(statement)

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Document]:
        statement = (
            select(Document)
            .order_by(Document.title.asc())
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
    ) -> list[Document]:
        statement = (
            select(Document)
            .where(Document.service_id == service_id)
            .order_by(Document.title.asc())
            .offset(skip)
            .limit(limit)
        )

        return list(
            db.scalars(statement).all()
        )

    @staticmethod
    def update(
        db: Session,
        document: Document,
        document_data: DocumentUpdate,
    ) -> Document:
        update_data = document_data.model_dump(
            exclude_unset=True,
            mode="json",
        )

        for field, value in update_data.items():
            setattr(document, field, value)

        db.commit()
        db.refresh(document)

        return document

    @staticmethod
    def delete(
        db: Session,
        document: Document,
    ) -> None:
        db.delete(document)
        db.commit()
