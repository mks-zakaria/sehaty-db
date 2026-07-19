"""Scheduling models: doctor availability windows and patient appointments."""

import enum
from datetime import date, datetime, time

from sqlalchemy import JSON, Date, DateTime, Enum, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from sehaty.db.base import SehatyBase, TimestampMixin


class AppointmentStatus(enum.StrEnum):
    REQUESTED = "REQUESTED"
    CONFIRMED = "CONFIRMED"
    # Secretary confirmed the patient is physically present and the (acting) doctor
    # is online at the cabinet: the visit is now in the doctor's waiting queue.
    CHECKED_IN = "CHECKED_IN"
    # The doctor has started the consultation (consultation_started_at is set).
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"


class AvailabilityExceptionKind(enum.StrEnum):
    # Closed that day or for a specific time range (vacation/holiday).
    BLOCK = "BLOCK"
    # Extra one-off availability on that day (outside the recurring weekly schedule).
    OPEN = "OPEN"
    # Daily patient cap for that date: accept at most ``max_patients`` bookings.
    CAP = "CAP"


class Availability(SehatyBase):
    """Recurring weekly bookable window for a doctor."""

    __tablename__ = "availabilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    weekday: Mapped[int] = mapped_column(Integer)  # 0=Monday .. 6=Sunday
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    slot_minutes: Mapped[int] = mapped_column(Integer, default=30)


class AvailabilityException(SehatyBase, TimestampMixin):
    """Date-specific override of a doctor's recurring weekly availability.

    BLOCK closes the day (NULL start/end = whole day, otherwise the given window).
    OPEN adds one-off availability on that day (start/end + slot_minutes define it).
    CAP limits that date to ``max_patients`` bookings (start/end/slot are unused).
    """

    __tablename__ = "availability_exceptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)  # the specific calendar day
    kind: Mapped[AvailabilityExceptionKind] = mapped_column(
        Enum(AvailabilityExceptionKind, name="availability_exception_kind")
    )
    # Affected window. NULL start/end on a BLOCK = the whole day.
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    # Slot length for OPEN windows.
    slot_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Max bookings for a CAP exception (NULL for BLOCK/OPEN).
    max_patients: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Appointment(SehatyBase, TimestampMixin):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus, name="appointment_status"),
        default=AppointmentStatus.REQUESTED,
    )
    reason: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(String(1000))
    # Timestamp the patient reminder was sent (NULL = not yet reminded). Used to
    # make reminder delivery idempotent so a reminder isn't sent twice.
    reminder_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Link to the doctor's patient register (clinic_patients). Nullable so historic
    # rows and new bookings without a register entry still validate; the migration
    # backfills existing appointments.
    clinic_patient_id: Mapped[int | None] = mapped_column(
        ForeignKey("clinic_patients.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # The cabinet session (a doctor's open shift) this visit was handled in. The
    # session carries the ACTING doctor, which may differ from ``doctor_id`` when a
    # substitute/locum covers for the owner. NULL for appointments booked/handled
    # outside a cabinet session (e.g. historic rows).
    cabinet_session_id: Mapped[int | None] = mapped_column(
        ForeignKey("cabinet_sessions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # --- Consultation record (the encounter), filled in by the doctor at the desk.
    # The scheduled slot is ``start_at``/``end_at``; these are the ACTUAL times the
    # doctor started and finished seeing the patient.
    consultation_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    consultation_ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # The patient's presenting complaint in their own words (free text).
    chief_complaint: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    # Structured symptoms captured during the visit (list/dict), JSON for training.
    symptoms: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Structured vitals (e.g. {"bp": "120/80", "temp_c": 37.2, "hr": 72}), JSON.
    vitals: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # The doctor's examination findings / consultation notes (free text).
    exam_notes: Mapped[str | None] = mapped_column(String(4000), nullable=True)
