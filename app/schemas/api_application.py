from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class APIApplicationCreate(BaseModel):
    company_name: str = Field(
        min_length=2,
        max_length=200,
    )

    contact_name: str = Field(
        min_length=2,
        max_length=150,
    )

    email: EmailStr

    website: HttpUrl | None = None

    purpose: str = Field(
        min_length=10,
        max_length=2000,
    )


class APIApplicationRegistrationResponse(BaseModel):
    id: int
    company_name: str
    contact_name: str
    email: EmailStr
    website: str | None
    purpose: str
    api_key: str
    api_key_prefix: str
    is_active: bool
    created_at: datetime
    message: str


class APIApplicationResponse(BaseModel):
    id: int
    company_name: str
    contact_name: str
    email: EmailStr
    website: str | None
    purpose: str
    api_key_prefix: str
    is_active: bool
    request_count: int
    last_used_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)