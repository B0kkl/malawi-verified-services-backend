from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.models.base import BaseModel


class APIApplication(BaseModel):
    __tablename__ = "api_applications"

    company_name = Column(
        String(200),
        nullable=False,
        index=True,
    )

    contact_name = Column(
        String(150),
        nullable=False,
    )

    email = Column(
        String(255),
        nullable=False,
        index=True,
    )

    website = Column(
        String(500),
        nullable=True,
    )

    purpose = Column(
        Text,
        nullable=False,
    )

    api_key_prefix = Column(
        String(32),
        nullable=False,
        index=True,
    )

    api_key_hash = Column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="1",
    )

    request_count = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    last_used_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )