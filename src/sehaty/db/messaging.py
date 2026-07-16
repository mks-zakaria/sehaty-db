"""Messaging models: 1:1 patient<->clinic threads and their messages."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sehaty.db.base import SehatyBase, TimestampMixin


class MessageThread(SehatyBase, TimestampMixin):
    """A 1:1 conversation between a patient and a doctor (the clinic side)."""

    __tablename__ = "message_threads"
    __table_args__ = (
        # One thread per patient<->doctor pair.
        UniqueConstraint("patient_id", "doctor_id", name="uq_message_threads_patient_doctor"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    # Denormalised timestamp of the latest message, for inbox sorting (indexed).
    last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    # Per-side read watermarks used to compute unread counts.
    patient_last_read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    doctor_last_read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )


class Message(SehatyBase):
    """A single message belonging to a thread."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    thread_id: Mapped[int] = mapped_column(
        ForeignKey("message_threads.id", ondelete="CASCADE"), index=True
    )
    # The actual author: patient, doctor, or the doctor's assistant acting for the clinic.
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    thread: Mapped["MessageThread"] = relationship(back_populates="messages")
