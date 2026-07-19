from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel
from app.models.base import Base

class Agency(BaseModel):
    contacts = relationship(
        "Contact",
        back_populates="agency",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    services = relationship(
        "Service",
        back_populates="agency",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    __tablename__ = "agencies"

    name = Column(String(200), nullable=False, index=True)

    short_name = Column(String(100))

    category = Column(String(100), nullable=False)

    country = Column(String(100), nullable=False)

    city = Column(String(100))

    address = Column(String(300))

    website = Column(String(255))

    description = Column(String(1000))

    is_active = Column(Boolean, default=True)