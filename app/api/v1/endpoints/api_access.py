from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.api_application import (
    APIApplicationCreate,
    APIApplicationRegistrationResponse,
)
from app.services.api_application_service import APIApplicationService


router = APIRouter(
    prefix="/api-access",
    tags=["API Access"],
)


@router.post(
    "/register",
    response_model=APIApplicationRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_api_application(
    application_data: APIApplicationCreate,
    db: Session = Depends(get_db),
):
    return APIApplicationService.register_application(
        db=db,
        application_data=application_data,
    )