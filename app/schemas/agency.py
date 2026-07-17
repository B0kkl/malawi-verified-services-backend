from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AgencyBase(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    short_name: str | None = Field(default=None, max_length=100)
    category: str = Field(min_length=2, max_length=100)
    country: str = Field(min_length=2, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=300)
    website: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    is_active: bool = True


class AgencyCreate(AgencyBase):
    pass


class AgencyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    short_name: str | None = Field(default=None, max_length=100)
    category: str | None = Field(default=None, min_length=2, max_length=100)
    country: str | None = Field(default=None, min_length=2, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=300)
    website: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    is_active: bool | None = None


class AgencyResponse(AgencyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)