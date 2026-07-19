from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Requirement(BaseModel):
    __tablename__ = "requirements"

    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_mandatory: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    service = relationship(
        "Service",
        back_populates="requirement_items",
    )
