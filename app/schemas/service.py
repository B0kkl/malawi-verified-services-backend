from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class ServiceBase(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    category: str | None = Field(default=None, max_length=100)
    description: str | None = None

    requirements: str | None = None
    application_process: str | None = None
    processing_time: str | None = Field(default=None, max_length=150)

    fee_amount: Decimal | None = Field(default=None, ge=0)
    fee_currency: str = Field(default="MWK", min_length=3, max_length=10)

    office_location: str | None = Field(default=None, max_length=255)
    online_available: bool = False
    online_url: HttpUrl | None = None

    contact_phone: str | None = Field(default=None, max_length=50)
    contact_email: EmailStr | None = None

    is_active: bool = True


class ServiceCreate(ServiceBase):
    agency_id: int = Field(gt=0)


class ServiceUpdate(BaseModel):
    agency_id: int | None = Field(default=None, gt=0)

    name: str | None = Field(default=None, min_length=2, max_length=200)
    category: str | None = Field(default=None, max_length=100)
    description: str | None = None

    requirements: str | None = None
    application_process: str | None = None
    processing_time: str | None = Field(default=None, max_length=150)

    fee_amount: Decimal | None = Field(default=None, ge=0)
    fee_currency: str | None = Field(default=None, min_length=3, max_length=10)

    office_location: str | None = Field(default=None, max_length=255)
    online_available: bool | None = None
    online_url: HttpUrl | None = None

    contact_phone: str | None = Field(default=None, max_length=50)
    contact_email: EmailStr | None = None

    is_active: bool | None = None


class ServiceResponse(ServiceBase):
    id: int
    agency_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)