from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactBase(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=150,
    )
    job_title: str | None = Field(
        default=None,
        max_length=150,
    )
    department: str | None = Field(
        default=None,
        max_length=150,
    )
    phone_number: str | None = Field(
        default=None,
        max_length=50,
    )
    alternative_phone: str | None = Field(
        default=None,
        max_length=50,
    )
    email: EmailStr | None = None
    office_hours: str | None = Field(
        default=None,
        max_length=150,
    )
    notes: str | None = None
    is_primary: bool = False
    is_active: bool = True


class ContactCreate(ContactBase):
    agency_id: int = Field(gt=0)


class ContactUpdate(BaseModel):
    agency_id: int | None = Field(
        default=None,
        gt=0,
    )
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )
    job_title: str | None = Field(
        default=None,
        max_length=150,
    )
    department: str | None = Field(
        default=None,
        max_length=150,
    )
    phone_number: str | None = Field(
        default=None,
        max_length=50,
    )
    alternative_phone: str | None = Field(
        default=None,
        max_length=50,
    )
    email: EmailStr | None = None
    office_hours: str | None = Field(
        default=None,
        max_length=150,
    )
    notes: str | None = None
    is_primary: bool | None = None
    is_active: bool | None = None


class ContactResponse(ContactBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agency_id: int
    created_at: datetime
    updated_at: datetime