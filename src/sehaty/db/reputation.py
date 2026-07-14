"""Two-way public ratings (patient<->doctor), booking-gated + moderation queue."""

import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from sehaty.db.base import SehatyBase, TimestampMixin


class ReviewDirection(enum.StrEnum):
    PATIENT_ON_DOCTOR = "PATIENT_ON_DOCTOR"
    DOCTOR_ON_PATIENT = "DOCTOR_ON_PATIENT"


class ReviewStatus(enum.StrEnum):
    PENDING = "PENDING"
    PUBLISHED = "PUBLISHED"
    FLAGGED = "FLAGGED"
    REMOVED = "REMOVED"


class Review(SehatyBase, TimestampMixin):
    __tablename__ = "reviews"
    __table_args__ = (
        # Anti-gaming: at most one review per author per appointment per direction.
        UniqueConstraint(
            "author_id",
            "appointment_id",
            "direction",
            name="uq_review_author_appointment_direction",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    target_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    # Booking gate: a review requires a (completed) appointment.
    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointments.id", ondelete="CASCADE"), index=True
    )
    direction: Mapped[ReviewDirection] = mapped_column(
        Enum(ReviewDirection, name="review_direction")
    )
    # Range 1..5 enforced at the app layer; column is a plain int.
    stars: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(String(2000))
    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, name="review_status"), default=ReviewStatus.PENDING
    )
    # Right-of-reply for the rated party.
    reply: Mapped[str | None] = mapped_column(String(2000))
    reply_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ReputationScore(SehatyBase):
    """Materialized aggregate per user, refreshed by core."""

    __tablename__ = "reputation_scores"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    avg_stars: Mapped[float] = mapped_column(Float, default=0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
