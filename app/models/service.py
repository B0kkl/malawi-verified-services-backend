from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Service(BaseModel):
    __tablename__ = "services"

    agency_id = Column(
        Integer,
        ForeignKey("agencies.id"),
        nullable=False,
        index=True,
    )

    name = Column(String(255), nullable=False)
    category = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)

    # Existing legacy summary field.
    requirements = Column(Text, nullable=True)

    application_process = Column(Text, nullable=True)
    processing_time = Column(String(150), nullable=True)
    fee_amount = Column(Numeric(12, 2), nullable=True, default=0)
    fee_currency = Column(String(10), nullable=False, default="MWK")
    office_location = Column(String(255), nullable=True)
    online_available = Column(Boolean, nullable=False, default=False)
    online_url = Column(String(500), nullable=True)
    contact_phone = Column(String(100), nullable=True)
    contact_email = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    agency = relationship(
        "Agency",
        back_populates="services",
    )

    requirement_items = relationship(
        "Requirement",
        back_populates="service",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    fee_items = relationship(
      "Fee",
        back_populates="service",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )