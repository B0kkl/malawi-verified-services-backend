from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class DocumentBase(BaseModel):
    title: str = Field(
        min_length=2,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    document_type: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    file_url: HttpUrl

    is_downloadable: bool = True


class DocumentCreate(DocumentBase):
    service_id: int = Field(gt=0)


class DocumentUpdate(BaseModel):
    service_id: int | None = Field(
        default=None,
        gt=0,
    )

    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    document_type: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    file_url: HttpUrl | None = None

    is_downloadable: bool | None = None


class DocumentResponse(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_id: int
    created_at: datetime
    updated_at: datetime
