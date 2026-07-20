from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class FeeBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=200,
    )

    amount: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    currency: str = Field(
        default="MWK",
        min_length=3,
        max_length=10,
    )

    description: str | None = None


class FeeCreate(FeeBase):
    service_id: int = Field(gt=0)


class FeeUpdate(BaseModel):
    service_id: int | None = Field(
        default=None,
        gt=0,
    )

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    amount: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=10,
    )

    description: str | None = None


class FeeResponse(FeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_id: int
    created_at: datetime
    updated_at: datetime
