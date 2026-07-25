import hashlib

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.api_application import APIApplication
from app.repositories.api_application_repository import (
    APIApplicationRepository,
)


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(
        api_key.encode("utf-8")
    ).hexdigest()


def require_api_application(
    x_api_key: str | None = Header(
        default=None,
        alias="X-API-Key",
    ),
    db: Session = Depends(get_db),
) -> APIApplication:
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header is required.",
        )

    api_key_hash = hash_api_key(x_api_key)

    application = APIApplicationRepository.get_by_api_key_hash(
        db=db,
        api_key_hash=api_key_hash,
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )

    if not application.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This API application has been deactivated.",
        )

    APIApplicationRepository.record_usage(
        db=db,
        application=application,
    )

    return application