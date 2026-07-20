from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.faq import (
    FAQCreate,
    FAQResponse,
    FAQUpdate,
)
from app.services.faq_service import FAQService


router = APIRouter(
    prefix="/faqs",
    tags=["FAQs"],
)


@router.post(
    "",
    response_model=FAQResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_faq(
    faq_data: FAQCreate,
    db: Session = Depends(get_db),
):
    return FAQService.create_faq(
        db=db,
        faq_data=faq_data,
    )


@router.get(
    "",
    response_model=list[FAQResponse],
)
def get_faqs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return FAQService.get_faqs(
        db=db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/service/{service_id}",
    response_model=list[FAQResponse],
)
def get_service_faqs(
    service_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return FAQService.get_service_faqs(
        db=db,
        service_id=service_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{faq_id}",
    response_model=FAQResponse,
)
def get_faq(
    faq_id: int,
    db: Session = Depends(get_db),
):
    return FAQService.get_faq(
        db=db,
        faq_id=faq_id,
    )


@router.patch(
    "/{faq_id}",
    response_model=FAQResponse,
)
def update_faq(
    faq_id: int,
    faq_data: FAQUpdate,
    db: Session = Depends(get_db),
):
    return FAQService.update_faq(
        db=db,
        faq_id=faq_id,
        faq_data=faq_data,
    )


@router.delete(
    "/{faq_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_faq(
    faq_id: int,
    db: Session = Depends(get_db),
):
    FAQService.delete_faq(
        db=db,
        faq_id=faq_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
