from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Location(BaseModel):
    __tablename__ = "locations"

    agency_id: Mapped[int] = mapped_column(
        ForeignKey("agencies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    district: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    physical_address: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    postal_address: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    is_head_office: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    agency = relationship(
        "Agency",
        back_populates="locations",
    )
