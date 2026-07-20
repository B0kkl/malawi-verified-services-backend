from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.fee import Fee
from app.repositories.fee_repository import FeeRepository
from app.repositories.service_repository import ServiceRepository
from app.schemas.fee import FeeCreate, FeeUpdate


class FeeService:
    @staticmethod
    def create_fee(
        db: Session,
        fee_data: FeeCreate,
    ) -> Fee:
        service_repository = ServiceRepository(db)

        service = service_repository.get_by_id(
            fee_data.service_id
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        return FeeRepository.create(
            db,
            fee_data,
        )

    @staticmethod
    def get_fee(
        db: Session,
        fee_id: int,
    ) -> Fee:
        fee = FeeRepository.get_by_id(
            db,
            fee_id,
        )

        if fee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fee not found.",
            )

        return fee

    @staticmethod
    def get_fees(
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Fee]:
        return FeeRepository.get_all(
            db,
            skip,
            limit,
        )

    @staticmethod
    def get_service_fees(
        db: Session,
        service_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Fee]:
        service_repository = ServiceRepository(db)

        service = service_repository.get_by_id(
            service_id
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        return FeeRepository.get_by_service(
            db,
            service_id,
            skip,
            limit,
        )

    @staticmethod
    def update_fee(
        db: Session,
        fee_id: int,
        fee_data: FeeUpdate,
    ) -> Fee:
        fee = FeeService.get_fee(
            db,
            fee_id,
        )

        if fee_data.service_id is not None:
            service_repository = ServiceRepository(db)

            service = service_repository.get_by_id(
                fee_data.service_id
            )

            if service is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Service not found.",
                )

        return FeeRepository.update(
            db,
            fee,
            fee_data,
        )

    @staticmethod
    def delete_fee(
        db: Session,
        fee_id: int,
    ) -> None:
        fee = FeeService.get_fee(
            db,
            fee_id,
        )

        FeeRepository.delete(
            db,
            fee,
        )
