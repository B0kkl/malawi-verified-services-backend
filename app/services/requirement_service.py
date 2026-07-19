from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.requirement import Requirement
from app.repositories.requirement_repository import RequirementRepository
from app.repositories.service_repository import ServiceRepository
from app.schemas.requirement import RequirementCreate, RequirementUpdate


class RequirementService:
    @staticmethod
    def create_requirement(
        db: Session,
        requirement_data: RequirementCreate,
    ) -> Requirement:
        service_repository = ServiceRepository(db)

        service = service_repository.get_by_id(
            requirement_data.service_id
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        return RequirementRepository.create(
            db,
            requirement_data,
        )

    @staticmethod
    def get_requirement(
        db: Session,
        requirement_id: int,
    ) -> Requirement:
        requirement = RequirementRepository.get_by_id(
            db,
            requirement_id,
        )

        if requirement is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requirement not found.",
            )

        return requirement

    @staticmethod
    def get_requirements(
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Requirement]:
        return RequirementRepository.get_all(
            db,
            skip,
            limit,
        )

    @staticmethod
    def get_service_requirements(
        db: Session,
        service_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Requirement]:
        service_repository = ServiceRepository(db)

        service = service_repository.get_by_id(service_id)

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        return RequirementRepository.get_by_service(
            db,
            service_id,
            skip,
            limit,
        )

    @staticmethod
    def update_requirement(
        db: Session,
        requirement_id: int,
        requirement_data: RequirementUpdate,
    ) -> Requirement:
        requirement = RequirementService.get_requirement(
            db,
            requirement_id,
        )

        if requirement_data.service_id is not None:
            service_repository = ServiceRepository(db)

            service = service_repository.get_by_id(
                requirement_data.service_id
            )

            if service is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Service not found.",
                )

        return RequirementRepository.update(
            db,
            requirement,
            requirement_data,
        )

    @staticmethod
    def delete_requirement(
        db: Session,
        requirement_id: int,
    ) -> None:
        requirement = RequirementService.get_requirement(
            db,
            requirement_id,
        )

        RequirementRepository.delete(
            db,
            requirement,
        )
