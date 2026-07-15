"""Scheduling models: doctor availability windows and patient appointments."""

import enum
from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from sehaty.db.base import SehatyBase, TimestampMixin


class AppointmentStatus(enum.StrEnum):
    REQUESTED = "REQUESTED"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"


class AvailabilityExceptionKind(enum.StrEnum):
    # Closed that day or for a specific time range (vacation/holiday).
    BLOCK = "BLOCK"
    # Extra one-off availability on that day (outside the recurring weekly schedule).
    OPEN = "OPEN"


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
