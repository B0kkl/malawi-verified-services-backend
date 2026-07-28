from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload
from app.models.agency import Agency
from app.models.location import Location
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.models.agency import Agency

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
    
    def search(
        self,
        search: str | None = None,
        category: str | None = None,
        agency_id: int | None = None,
        district: str | None = None,
        online_available: bool | None = None,
        is_active: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Service]:

        query = (
            self.db.query(Service)
            .join(Agency)
            .outerjoin(Location)
        )

        if search:
            keyword = f"%{search}%"

            query = query.filter(
                or_(
                    Service.name.ilike(keyword),
                    Service.description.ilike(keyword),
                    Agency.name.ilike(keyword),
                )
            )

        if category:
            query = query.filter(
                Service.category == category
            )

        if agency_id:
            query = query.filter(
                Service.agency_id == agency_id
            )

        if district:
            query = query.filter(
                Location.district == district
            )

        if online_available is not None:
            query = query.filter(
                Service.online_available == online_available
            )

        if is_active is not None:
            query = query.filter(
                Service.is_active == is_active
            )

        return (
            query.distinct()
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


    def get_details(self, service_id: int) -> Service | None:
        return (
            self.db.query(Service)
            .options(
                selectinload(Service.agency).selectinload(
                    Agency.contacts
                ),
                selectinload(Service.agency).selectinload(
                    Agency.locations
                ),
                selectinload(Service.requirement_items),
                selectinload(Service.fee_items),
                selectinload(Service.faq_items),
                selectinload(Service.document_items),
            )
            .filter(Service.id == service_id)
            .first()
            )