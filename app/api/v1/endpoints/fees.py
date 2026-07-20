from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.fee import (
    FeeCreate,
    FeeResponse,
    FeeUpdate,
)
from app.services.fee_service import FeeService


router = APIRouter(
    prefix="/fees",
    tags=["Fees"],
)


@router.post(
    "",
    response_model=FeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_fee(
    fee_data: FeeCreate,
    db: Session = Depends(get_db),
):
    return FeeService.create_fee(
        db=db,
        fee_data=fee_data,
    )


@router.get(
    "",
    response_model=list[FeeResponse],
)
def get_fees(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return FeeService.get_fees(
        db=db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/service/{service_id}",
    response_model=list[FeeResponse],
)
def get_service_fees(
    service_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return FeeService.get_service_fees(
        db=db,
        service_id=service_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{fee_id}",
    response_model=FeeResponse,
)
def get_fee(
    fee_id: int,
    db: Session = Depends(get_db),
):
    return FeeService.get_fee(
        db=db,
        fee_id=fee_id,
    )


@router.patch(
    "/{fee_id}",
    response_model=FeeResponse,
)
def update_fee(
    fee_id: int,
    fee_data: FeeUpdate,
    db: Session = Depends(get_db),
):
    return FeeService.update_fee(
        db=db,
        fee_id=fee_id,
        fee_data=fee_data,
    )


@router.delete(
    "/{fee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_fee(
    fee_id: int,
    db: Session = Depends(get_db),
):
    FeeService.delete_fee(
        db=db,
        fee_id=fee_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
