from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.api_application import APIApplication
from app.schemas.api_application import APIApplicationCreate


class APIApplicationRepository:
    @staticmethod
    def create(
        db: Session,
        application_data: APIApplicationCreate,
        api_key_prefix: str,
        api_key_hash: str,
    ) -> APIApplication:
        data = application_data.model_dump(mode="json")

        application = APIApplication(
            **data,
            api_key_prefix=api_key_prefix,
            api_key_hash=api_key_hash,
        )

        db.add(application)
        db.commit()
        db.refresh(application)

        return application

    @staticmethod
    def get_by_id(
        db: Session,
        application_id: int,
    ) -> APIApplication | None:
        statement = select(APIApplication).where(
            APIApplication.id == application_id
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_api_key_hash(
        db: Session,
        api_key_hash: str,
    ) -> APIApplication | None:
        statement = select(APIApplication).where(
            APIApplication.api_key_hash == api_key_hash
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ) -> list[APIApplication]:
        statement = (
            select(APIApplication)
            .where(APIApplication.email == email)
            .order_by(APIApplication.created_at.desc())
        )

        return list(db.scalars(statement).all())

    @staticmethod
    def record_usage(
        db: Session,
        application: APIApplication,
    ) -> APIApplication:
        application.request_count += 1
        application.last_used_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(application)

        return application

    @staticmethod
    def revoke(
        db: Session,
        application: APIApplication,
    ) -> APIApplication:
        application.is_active = False

        db.commit()
        db.refresh(application)

        return application