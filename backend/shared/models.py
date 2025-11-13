"""
Shared SQLAlchemy models and mixins
"""
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.sql import func


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps"""

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class IDMixin:
    """Mixin to add auto-incrementing ID primary key"""

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
