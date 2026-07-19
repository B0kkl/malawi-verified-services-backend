from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LocationBase(BaseModel):
    district: str = Field(
        min_length=2,
        max_length=100,
    )

    physical_address: str = Field(
        min_length=2,
    )

    postal_address: str | None = Field(
        default=None,
        max_length=255,
    )

    phone_number: str | None = Field(
        default=None,
        max_length=50,
    )

    email: EmailStr | None = None

    is_head_office: bool = False


class LocationCreate(LocationBase):
    agency_id: int = Field(gt=0)


class LocationUpdate(BaseModel):
    agency_id: int | None = Field(
        default=None,
        gt=0,
    )

    district: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    physical_address: str | None = Field(
        default=None,
        min_length=2,
    )

    postal_address: str | None = Field(
        default=None,
        max_length=255,
    )

    phone_number: str | None = Field(
        default=None,
        max_length=50,
    )

    email: EmailStr | None = None

    is_head_office: bool | None = None


class LocationResponse(LocationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agency_id: int
    created_at: datetime
    updated_at: datetime
