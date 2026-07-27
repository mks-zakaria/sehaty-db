"""Per-doctor waitlist: patients who want a slot if one frees up.

This is the half that makes no-show detection worth paying for. Knowing a
patient will not come is only useful if someone else takes the slot; without a
waitlist, the confirmation system is a nicer way to watch money leave.

Entries are per doctor, not per slot: a patient says "tell me if anything opens
with Dr X", and the first freed slot that fits is offered to whoever has been
waiting longest.
"""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from sehaty.db.base import SehatyBase, TimestampMixin, utcnow


class WaitlistStatus(enum.StrEnum):
    # Waiting for something to open.
    WAITING = "WAITING"
    # A slot was offered and the patient has not answered yet. Time-boxed: an
    # unanswered offer must expire, or one slow reply blocks the whole queue
    # while the slot stays empty.
    OFFERED = "OFFERED"
    # Took the slot.
    ACCEPTED = "ACCEPTED"
    # Turned it down, or the offer timed out. Stays on the list for the next one.
    PASSED = "PASSED"
    # Left the list.
    CANCELLED = "CANCELLED"


class WaitlistEntry(SehatyBase, TimestampMixin):
    """One patient waiting for an earlier slot with one doctor."""

    __tablename__ = "waitlist_entries"
    __table_args__ = (
        # A patient waits once per doctor; asking twice must not double their
        # odds or send them two offers for the same slot.
        UniqueConstraint("doctor_id", "patient_id", name="uq_waitlist_doctor_patient"),
        # The offer query: this doctor's waiting entries, oldest first.
        Index("ix_waitlist_doctor_status_created", "doctor_id", "status", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[WaitlistStatus] = mapped_column(
        Enum(WaitlistStatus, name="waitlist_status"), default=WaitlistStatus.WAITING
    )
    # Earliest date the patient can attend; NULL means "anything".
    earliest_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Latest useful date — past it the entry stops being offered rather than
    # sitting in the queue forever proposing slots nobody wants.
    latest_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # The appointment currently offered to this patient, if any.
    offered_appointment_id: Mapped[int | None] = mapped_column(
        ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True
    )
    offered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    note: Mapped[str | None] = mapped_column(String(300), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
