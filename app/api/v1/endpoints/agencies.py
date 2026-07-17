from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.agency import AgencyCreate, AgencyResponse, AgencyUpdate
from app.services.agency_service import AgencyService


router = APIRouter(
    prefix="/agencies",
    tags=["Agencies"],
)


@router.post(
    "",
    response_model=AgencyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_agency(
    agency_data: AgencyCreate,
    db: Session = Depends(get_db),
):
    return AgencyService.create_agency(
        db=db,
        agency_data=agency_data,
    )


@router.get(
    "",
    response_model=list[AgencyResponse],
)
def get_agencies(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return AgencyService.get_agencies(
        db=db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{agency_id}",
    response_model=AgencyResponse,
)
def get_agency(
    agency_id: int,
    db: Session = Depends(get_db),
):
    return AgencyService.get_agency(
        db=db,
        agency_id=agency_id,
    )


@router.patch(
    "/{agency_id}",
    response_model=AgencyResponse,
)
def update_agency(
    agency_id: int,
    agency_data: AgencyUpdate,
    db: Session = Depends(get_db),
):
    return AgencyService.update_agency(
        db=db,
        agency_id=agency_id,
        agency_data=agency_data,
    )


@router.delete(
    "/{agency_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_agency(
    agency_id: int,
    db: Session = Depends(get_db),
):
    AgencyService.delete_agency(
        db=db,
        agency_id=agency_id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)