from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RequirementBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=200,
    )

    description: str | None = None

    is_mandatory: bool = True


class RequirementCreate(RequirementBase):
    service_id: int = Field(gt=0)


class RequirementUpdate(BaseModel):
    service_id: int | None = Field(
        default=None,
        gt=0,
    )

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    description: str | None = None

    is_mandatory: bool | None = None


class RequirementResponse(RequirementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_id: int
    created_at: datetime
    updated_at: datetime
