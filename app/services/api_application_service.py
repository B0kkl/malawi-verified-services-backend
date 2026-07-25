import hashlib
import secrets

from sqlalchemy.orm import Session

from app.models.api_application import APIApplication
from app.repositories.api_application_repository import (
    APIApplicationRepository,
)
from app.schemas.api_application import (
    APIApplicationCreate,
    APIApplicationRegistrationResponse,
)


class APIApplicationService:
    API_KEY_PREFIX = "mvs_live_"

    @staticmethod
    def generate_api_key() -> str:
        random_part = secrets.token_urlsafe(32)
        return f"{APIApplicationService.API_KEY_PREFIX}{random_part}"

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        return hashlib.sha256(
            api_key.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def get_display_prefix(api_key: str) -> str:
        return api_key[:16]

    @staticmethod
    def register_application(
        db: Session,
        application_data: APIApplicationCreate,
    ) -> APIApplicationRegistrationResponse:
        api_key = APIApplicationService.generate_api_key()
        api_key_hash = APIApplicationService.hash_api_key(api_key)
        api_key_prefix = APIApplicationService.get_display_prefix(api_key)

        application: APIApplication = APIApplicationRepository.create(
            db=db,
            application_data=application_data,
            api_key_prefix=api_key_prefix,
            api_key_hash=api_key_hash,
        )

        return APIApplicationRegistrationResponse(
            id=application.id,
            company_name=application.company_name,
            contact_name=application.contact_name,
            email=application.email,
            website=application.website,
            purpose=application.purpose,
            api_key=api_key,
            api_key_prefix=application.api_key_prefix,
            is_active=application.is_active,
            created_at=application.created_at,
            message=(
                "API application registered successfully. "
                "Copy and store this API key securely because "
                "it will not be shown again."
            ),
        )