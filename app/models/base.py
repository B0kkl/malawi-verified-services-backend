from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.sql import func

from app.database.session import Base


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class BaseModel(Base, TimestampMixin):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)