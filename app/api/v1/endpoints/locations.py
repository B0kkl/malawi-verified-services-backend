from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.location import (
    LocationCreate,
    LocationResponse,
    LocationUpdate,
)
from app.services.location_service import LocationService


router = APIRouter(
    prefix="/locations",
    tags=["Locations"],
)


@router.post(
    "",
    response_model=LocationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_location(
    location_data: LocationCreate,
    db: Session = Depends(get_db),
):
    return LocationService.create_location(
        db=db,
        location_data=location_data,
    )


@router.get(
    "",
    response_model=list[LocationResponse],
)
def get_locations(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return LocationService.get_locations(
        db=db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/agency/{agency_id}",
    response_model=list[LocationResponse],
)
def get_agency_locations(
    agency_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return LocationService.get_agency_locations(
        db=db,
        agency_id=agency_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{location_id}",
    response_model=LocationResponse,
)
def get_location(
    location_id: int,
    db: Session = Depends(get_db),
):
    return LocationService.get_location(
        db=db,
        location_id=location_id,
    )


@router.patch(
    "/{location_id}",
    response_model=LocationResponse,
)
def update_location(
    location_id: int,
    location_data: LocationUpdate,
    db: Session = Depends(get_db),
):
    return LocationService.update_location(
        db=db,
        location_id=location_id,
        location_data=location_data,
    )


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
):
    LocationService.delete_location(
        db=db,
        location_id=location_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
