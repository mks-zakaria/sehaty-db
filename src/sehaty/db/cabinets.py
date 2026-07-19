"""Cabinet (physical practice) models: cabinets and cabinet sessions.

A **cabinet** is a solo doctor's practice room. It is owned by one doctor and
staffed by that doctor's secretaries (the ``doctor_assistants`` links). Most of
the time the owner works the cabinet, but sometimes a colleague (a "friend in the
field") covers for them — a *substitute* / locum.

A **cabinet session** is one open shift: a doctor (the owner OR a substitute) is
physically present and "online" from ``opened_at`` until ``closed_at``. While
``is_open`` is true the secretary can check patients in against this session, and
those check-ins notify the session's *acting* doctor. A substitute shift is simply
a session whose ``acting_doctor_id`` differs from the cabinet's ``owner_doctor_id``.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from sehaty.db.base import SehatyBase, TimestampMixin


class Cabinet(SehatyBase, TimestampMixin):
    __tablename__ = "cabinets"

    id: Mapped[int] = mapped_column(primary_key=True)
    # The doctor who owns the practice. Cabinet disappears if the account is deleted.
    owner_doctor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200))
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Soft on/off toggle so a cabinet can be retired without deleting its history.
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true"), default=True
    )
    # How many people are physically in the waiting room right now — maintained by
    # the secretary (independent of the CHECKED_IN appointment queue).
    waiting_room_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0"), default=0
    )
    # Doctor-set alert threshold: when waiting_room_count reaches this and the
    # doctor isn't online at the cabinet, notify them to head in. NULL = no alert.
    waiting_alert_threshold: Mapped[int | None] = mapped_column(Integer, nullable=True)


class CabinetSession(SehatyBase, TimestampMixin):
    """One open shift at a cabinet, worked by the owner or a substitute doctor."""

    __tablename__ = "cabinet_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    cabinet_id: Mapped[int] = mapped_column(
        ForeignKey("cabinets.id", ondelete="CASCADE"), index=True
    )
    # The doctor actually present for this shift — the owner, or a substitute/locum
    # covering for them (substitute iff acting_doctor_id != cabinet.owner_doctor_id).
    acting_doctor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # True while the shift is live — the doctor is "online" at the cabinet and the
    # secretary can check patients in against this session.
    is_open: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true"), default=True, index=True
    )
