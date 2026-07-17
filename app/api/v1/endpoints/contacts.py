from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.contact import (
    ContactCreate,
    ContactResponse,
    ContactUpdate,
)
from app.services.contact_service import ContactService


router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"],
)


@router.post(
    "",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contact(
    contact_data: ContactCreate,
    db: Session = Depends(get_db),
):
    return ContactService.create_contact(
        db=db,
        contact_data=contact_data,
    )


@router.get(
    "",
    response_model=list[ContactResponse],
)
def get_contacts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return ContactService.get_contacts(
        db=db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/agency/{agency_id}",
    response_model=list[ContactResponse],
)
def get_agency_contacts(
    agency_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return ContactService.get_agency_contacts(
        db=db,
        agency_id=agency_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
):
    return ContactService.get_contact(
        db=db,
        contact_id=contact_id,
    )


@router.patch(
    "/{contact_id}",
    response_model=ContactResponse,
)
def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    db: Session = Depends(get_db),
):
    return ContactService.update_contact(
        db=db,
        contact_id=contact_id,
        contact_data=contact_data,
    )


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
):
    ContactService.delete_contact(
        db=db,
        contact_id=contact_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )