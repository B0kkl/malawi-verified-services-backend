from sqlalchemy.orm import Session

from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate


class ServiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, service_data: ServiceCreate) -> Service:
        data = service_data.model_dump(mode="json")

        service = Service(**data)

        self.db.add(service)

        try:
            self.db.commit()
            self.db.refresh(service)
            return service
        except Exception:
            self.db.rollback()
            raise

    def get_by_id(self, service_id: int) -> Service | None:
        return (
            self.db.query(Service)
            .filter(Service.id == service_id)
            .first()
        )

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Service]:
        return (
            self.db.query(Service)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_agency(
        self,
        agency_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Service]:
        return (
            self.db.query(Service)
            .filter(Service.agency_id == agency_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_name_and_agency(
        self,
        name: str,
        agency_id: int,
    ) -> Service | None:
        return (
            self.db.query(Service)
            .filter(
                Service.name == name,
                Service.agency_id == agency_id,
            )
            .first()
        )

    def update(
        self,
        service: Service,
        service_data: ServiceUpdate,
    ) -> Service:
        update_data = service_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(service, field, value)

        self.db.commit()
        self.db.refresh(service)

        return service

    def delete(self, service: Service) -> None:
        self.db.delete(service)
        self.db.commit()