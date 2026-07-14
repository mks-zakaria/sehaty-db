"""Admin/config models: generic key/value store, feature flags, ranking weights."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from sehaty.db.base import SehatyBase, TimestampMixin


class AdminConfig(SehatyBase, TimestampMixin):
    """Generic key/value config store; ``value`` holds JSON-encoded data."""

    __tablename__ = "admin_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    value: Mapped[str] = mapped_column(String)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class FeatureFlag(SehatyBase, TimestampMixin):
    """Named boolean toggle for gating product features."""

    __tablename__ = "feature_flags"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(String(512))


class RankingWeights(SehatyBase, TimestampMixin):
    """Admin-tunable weights for the doctor-locator ranking formula (single-row-ish)."""

    __tablename__ = "ranking_weights"

    id: Mapped[int] = mapped_column(primary_key=True)
    w_rating: Mapped[float] = mapped_column(Float, default=1.0)
    w_distance: Mapped[float] = mapped_column(Float, default=1.0)
    w_responsiveness: Mapped[float] = mapped_column(Float, default=0.5)
    w_verified: Mapped[float] = mapped_column(Float, default=0.5)
    w_recency: Mapped[float] = mapped_column(Float, default=0.25)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
