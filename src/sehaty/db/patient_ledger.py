"""Per-patient treatment ledger: charges paid off in instalments.

A doctor records a treatment charge (e.g. braces at 8000 MAD) against a
clinic_patients register row, then records payments against that charge over
time; the outstanding balance is always derived (total - sum(payments)), never
stored. Payments are append-only rows so the payment history is auditable.
"""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sehaty.db.base import SehatyBase, TimestampMixin


class PaymentMethod(enum.StrEnum):
    CASH = "CASH"
    CARD = "CARD"
    TRANSFER = "TRANSFER"
    CHEQUE = "CHEQUE"
    OTHER = "OTHER"


class PatientCharge(SehatyBase, TimestampMixin):
    """One billable treatment for one register patient (doctor-scoped)."""

    __tablename__ = "patient_charges"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Owning doctor — the ledger disappears with the doctor account.
    doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    clinic_patient_id: Mapped[int] = mapped_column(
        ForeignKey("clinic_patients.id", ondelete="CASCADE"), index=True
    )
    # What was done, e.g. "Braces — upper arch".
    label: Mapped[str] = mapped_column(String(200))
    total_amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), default="MAD")
    note: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    # Who recorded it (doctor or assistant); keep the row if they're removed.
    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    payments: Mapped[list["PatientPayment"]] = relationship(
        back_populates="charge", cascade="all, delete-orphan"
    )


class PatientPayment(SehatyBase, TimestampMixin):
    """One (partial) payment against a charge. Append-only."""

    __tablename__ = "patient_payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    charge_id: Mapped[int] = mapped_column(
        ForeignKey("patient_charges.id", ondelete="CASCADE"), index=True
    )
    amount: Mapped[float] = mapped_column(Float)
    method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, name="patient_payment_method"), default=PaymentMethod.CASH
    )
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    charge: Mapped["PatientCharge"] = relationship(back_populates="payments")
