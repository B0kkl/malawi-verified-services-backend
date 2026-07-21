from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
)
from app.services.document_service import DocumentService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    document_data: DocumentCreate,
    db: Session = Depends(get_db),
):
    return DocumentService.create_document(
        db=db,
        document_data=document_data,
    )


@router.get(
    "",
    response_model=list[DocumentResponse],
)
def get_documents(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return DocumentService.get_documents(
        db=db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/service/{service_id}",
    response_model=list[DocumentResponse],
)
def get_service_documents(
    service_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return DocumentService.get_service_documents(
        db=db,
        service_id=service_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    return DocumentService.get_document(
        db=db,
        document_id=document_id,
    )


@router.patch(
    "/{document_id}",
    response_model=DocumentResponse,
)
def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    db: Session = Depends(get_db),
):
    return DocumentService.update_document(
        db=db,
        document_id=document_id,
        document_data=document_data,
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    DocumentService.delete_document(
        db=db,
        document_id=document_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
