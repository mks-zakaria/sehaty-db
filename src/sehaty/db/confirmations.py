"""Appointment confirmation state and the outbound-message log.

The problem this exists to solve is the one doctors actually pay to fix: a
patient who does not turn up costs a whole consultation slot. Detecting that
early enough to refill the slot is worth more than detecting it accurately.

Timing is the design decision. A confirmation asked an hour ahead only tells you
the slot is already lost; asked 24 hours ahead it leaves the secretary time to
work the phone and sell the slot to somebody else. So the flow is:

    T-24h  ask the patient to confirm
    T-18h  still no reply -> flagged red for the secretary to call
    T-2h   plain reminder to the ones who confirmed

``OutboundMessage`` is a log, not a queue: one row per message actually sent,
for audit and per-doctor cost. It is separate from ``messaging.py``, which is
in-app doctor/patient threads.
"""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from sehaty.db.base import SehatyBase, TimestampMixin, utcnow


class ConfirmationStatus(enum.StrEnum):
    """Where a patient stands on turning up."""

    # Not asked yet, or asked and the window is still open.
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    # The patient actively said no — the most useful answer, since the slot can
    # be resold immediately rather than held.
    DECLINED = "DECLINED"
    # Asked, window elapsed, silence. Not the same as PENDING: silence after a
    # direct question is itself a signal.
    NO_REPLY = "NO_REPLY"


class ConfirmationChannel(enum.StrEnum):
    """How the confirmation was obtained."""

    # The secretary tapped a pre-filled wa.me link and sent it herself. This is
    # v1 — it needs no Meta Business verification and no per-message cost.
    WHATSAPP_MANUAL = "WHATSAPP_MANUAL"
    # Automated template message via the WhatsApp Cloud API.
    WHATSAPP_API = "WHATSAPP_API"
    SMS = "SMS"
    # Phoned, and the secretary recorded the answer.
    CALL = "CALL"


class OutboundStatus(enum.StrEnum):
    QUEUED = "QUEUED"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"
    FAILED = "FAILED"


class OutboundMessage(SehatyBase, TimestampMixin):
    """One message sent to a patient about an appointment.

    Kept for audit ("we did ask, here is when") and to attribute per-message
    cost to a doctor once the Cloud API is billing per conversation.
    """

    __tablename__ = "outbound_messages"
    __table_args__ = (
        Index("ix_outbound_messages_appt_sent", "appointment_id", "sent_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointments.id", ondelete="CASCADE"), index=True
    )
    channel: Mapped[ConfirmationChannel] = mapped_column(
        Enum(ConfirmationChannel, name="confirmation_channel")
    )
    # Approved template name for API sends (e.g. "appointment_confirm_fr"), or
    # NULL for a manual send where the secretary typed the text herself.
    template: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[OutboundStatus] = mapped_column(
        Enum(OutboundStatus, name="outbound_status"), default=OutboundStatus.QUEUED
    )
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
    # Provider's message id, for reconciling delivery webhooks back to this row.
    provider_message_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # Cost in thousandths of a centime, so per-message pricing stays exact in
    # integer arithmetic rather than drifting through floats.
    cost_micros: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error: Mapped[str | None] = mapped_column(String(400), nullable=True)
