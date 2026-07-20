from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FAQBase(BaseModel):
    question: str = Field(
        min_length=5,
        max_length=500,
    )

    answer: str = Field(
        min_length=2,
        max_length=5000,
    )


class FAQCreate(FAQBase):
    service_id: int = Field(gt=0)


class FAQUpdate(BaseModel):
    service_id: int | None = Field(
        default=None,
        gt=0,
    )

    question: str | None = Field(
        default=None,
        min_length=5,
        max_length=500,
    )

    answer: str | None = Field(
        default=None,
        min_length=2,
        max_length=5000,
    )


class FAQResponse(FAQBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_id: int
    created_at: datetime
    updated_at: datetime
