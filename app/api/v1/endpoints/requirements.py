from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.requirement import (
    RequirementCreate,
    RequirementResponse,
    RequirementUpdate,
)
from app.services.requirement_service import RequirementService


router = APIRouter(
    prefix="/requirements",
    tags=["Requirements"],
)


@router.post(
    "",
    response_model=RequirementResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_requirement(
    requirement_data: RequirementCreate,
    db: Session = Depends(get_db),
):
    return RequirementService.create_requirement(
        db=db,
        requirement_data=requirement_data,
    )


@router.get(
    "",
    response_model=list[RequirementResponse],
)
def get_requirements(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return RequirementService.get_requirements(
        db=db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/service/{service_id}",
    response_model=list[RequirementResponse],
)
def get_service_requirements(
    service_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return RequirementService.get_service_requirements(
        db=db,
        service_id=service_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{requirement_id}",
    response_model=RequirementResponse,
)
def get_requirement(
    requirement_id: int,
    db: Session = Depends(get_db),
):
    return RequirementService.get_requirement(
        db=db,
        requirement_id=requirement_id,
    )


@router.patch(
    "/{requirement_id}",
    response_model=RequirementResponse,
)
def update_requirement(
    requirement_id: int,
    requirement_data: RequirementUpdate,
    db: Session = Depends(get_db),
):
    return RequirementService.update_requirement(
        db=db,
        requirement_id=requirement_id,
        requirement_data=requirement_data,
    )


@router.delete(
    "/{requirement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_requirement(
    requirement_id: int,
    db: Session = Depends(get_db),
):
    RequirementService.delete_requirement(
        db=db,
        requirement_id=requirement_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
