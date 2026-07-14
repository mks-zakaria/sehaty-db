"""Single declarative base + timestamp helper for every Sehaty ORM model."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(UTC)


class SehatyBase(DeclarativeBase):
    """Declarative base for the whole schema (SQLAlchemy 2.0 style)."""

    def to_dict(self, *, exclude: set[str] | None = None) -> dict[str, Any]:
        exclude = exclude or set()
        return {c.name: getattr(self, c.name) for c in self.__table__.c if c.name not in exclude}

    def __repr__(self) -> str:
        keys = sorted(k for k in self.__dict__ if not k.startswith("_"))
        body = ", ".join(f"{k}={self.__dict__[k]!r}" for k in keys)
        return f"<{self.__class__.__name__}({body})>"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
