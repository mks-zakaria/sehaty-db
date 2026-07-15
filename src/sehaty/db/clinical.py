"""Clinical models: medication catalog, prescriptions, dispensing, and related trail."""

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sehaty.db.base import SehatyBase, TimestampMixin


class PrescriptionStatus(enum.StrEnum):
    ISSUED = "ISSUED"
    PARTIALLY_FULFILLED = "PARTIALLY_FULFILLED"
    FULFILLED = "FULFILLED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class InteractionSeverity(enum.StrEnum):
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    MAJOR = "MAJOR"


class RenewalStatus(enum.StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"


class TreatmentOutcome(enum.StrEnum):
    """How a patient reports they fared on a prescription/diagnosis/visit."""

    BETTER = "BETTER"
    SAME = "SAME"
    WORSE = "WORSE"


class Medication(SehatyBase):
    """Shared national medication catalog entry."""

    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(primary_key=True)
    inn_name: Mapped[str] = mapped_column(String(255), index=True)  # generic / INN
    brand_name: Mapped[str | None] = mapped_column(String(255), index=True)
    form: Mapped[str] = mapped_column(String(64))  # tablet, syrup, ...
    strength: Mapped[str | None] = mapped_column(String(64))  # e.g. 500mg
    atc_code: Mapped[str | None] = mapped_column(String(16), index=True)
    prescription_required: Mapped[bool] = mapped_column(Boolean, default=True)


class Prescription(SehatyBase, TimestampMixin):
    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    appointment_id: Mapped[int | None] = mapped_column(
        ForeignKey("appointments.id", ondelete="SET NULL")
    )
    # Which letterhead (practice profile) this was issued under. Kept if the
    # profile is later removed, so historical prescriptions stay printable.
    practice_profile_id: Mapped[int | None] = mapped_column(
        ForeignKey("practice_profiles.id", ondelete="SET NULL"), nullable=True
    )
    # Public verification code + opaque QR token.
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    qr_token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    status: Mapped[PrescriptionStatus] = mapped_column(
        Enum(PrescriptionStatus, name="prescription_status"),
        default=PrescriptionStatus.ISSUED,
    )
    # Free-text body / advice printed under the drug list.
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    items: Mapped[list["PrescriptionItem"]] = relationship(
        back_populates="prescription", cascade="all, delete-orphan"
    )


class PrescriptionItem(SehatyBase):
    __tablename__ = "prescription_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    prescription_id: Mapped[int] = mapped_column(
        ForeignKey("prescriptions.id", ondelete="CASCADE"), index=True
    )
    # Optional catalog link. NULL for freehand items a doctor types without the
    # national catalog; drug_name then carries the free-text drug.
    medication_id: Mapped[int | None] = mapped_column(ForeignKey("medications.id"), nullable=True)
    # Free-text drug name when there is no catalog id.
    drug_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dosage: Mapped[str] = mapped_column(String(128))  # e.g. "1 tablet"
    frequency: Mapped[str] = mapped_column(String(128))  # e.g. "twice a day"
    # Free-text posology / extra instructions.
    instructions: Mapped[str | None] = mapped_column(String(500), nullable=True)
    duration_days: Mapped[int | None] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)
    quantity_dispensed: Mapped[int] = mapped_column(Integer, default=0)

    prescription: Mapped["Prescription"] = relationship(back_populates="items")


class PharmacyStock(SehatyBase):
    __tablename__ = "pharmacy_stock"

    id: Mapped[int] = mapped_column(primary_key=True)
    pharmacy_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    medication_id: Mapped[int] = mapped_column(ForeignKey("medications.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    price: Mapped[float | None] = mapped_column(Float)
    low_threshold: Mapped[int] = mapped_column(Integer, default=10)


class Dispense(SehatyBase):
    __tablename__ = "dispenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    prescription_id: Mapped[int] = mapped_column(
        ForeignKey("prescriptions.id", ondelete="CASCADE"), index=True
    )
    pharmacy_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    dispensed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    notes: Mapped[str | None] = mapped_column(String(500))

    items: Mapped[list["DispenseItem"]] = relationship(
        back_populates="dispense", cascade="all, delete-orphan"
    )


class DispenseItem(SehatyBase):
    __tablename__ = "dispense_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    dispense_id: Mapped[int] = mapped_column(
        ForeignKey("dispenses.id", ondelete="CASCADE"), index=True
    )
    prescription_item_id: Mapped[int] = mapped_column(ForeignKey("prescription_items.id"))
    quantity: Mapped[int] = mapped_column(Integer)

    dispense: Mapped["Dispense"] = relationship(back_populates="items")


class DrugInteraction(SehatyBase):
    """A known interaction between two catalog medications.

    Stored once per unordered pair with the convention
    ``medication_id_a < medication_id_b``.
    """

    __tablename__ = "drug_interactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    medication_id_a: Mapped[int] = mapped_column(
        ForeignKey("medications.id", ondelete="CASCADE"), index=True
    )
    medication_id_b: Mapped[int] = mapped_column(
        ForeignKey("medications.id", ondelete="CASCADE"), index=True
    )
    severity: Mapped[InteractionSeverity] = mapped_column(
        Enum(InteractionSeverity, name="interaction_severity"),
        default=InteractionSeverity.MODERATE,
    )
    description: Mapped[str] = mapped_column(String(512))


class Notification(SehatyBase, TimestampMixin):
    """In-app notification delivered to a single recipient user."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    message: Mapped[str] = mapped_column(String(500))
    kind: Mapped[str] = mapped_column(String(32))
    entity: Mapped[str | None] = mapped_column(String(64))
    entity_id: Mapped[int | None] = mapped_column(Integer)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)


class RenewalRequest(SehatyBase, TimestampMixin):
    """A patient's request to have an existing prescription re-issued."""

    __tablename__ = "renewal_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    prescription_id: Mapped[int] = mapped_column(
        ForeignKey("prescriptions.id", ondelete="CASCADE"), index=True
    )
    patient_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[RenewalStatus] = mapped_column(
        Enum(RenewalStatus, name="renewal_status"),
        default=RenewalStatus.PENDING,
    )
    note: Mapped[str | None] = mapped_column(String(500))
    resulting_prescription_id: Mapped[int | None] = mapped_column(
        ForeignKey("prescriptions.id", ondelete="SET NULL")
    )


class Diagnosis(SehatyBase, TimestampMixin):
    """A disease/condition a doctor recorded for a register patient."""

    __tablename__ = "diagnoses"

    id: Mapped[int] = mapped_column(primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    # The register patient this diagnosis belongs to.
    clinic_patient_id: Mapped[int | None] = mapped_column(
        ForeignKey("clinic_patients.id", ondelete="SET NULL"), nullable=True, index=True
    )
    appointment_id: Mapped[int | None] = mapped_column(
        ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True
    )
    # The disease/condition, free text.
    label: Mapped[str] = mapped_column(String(255))
    icd10: Mapped[str | None] = mapped_column(String(16), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    diagnosed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class TreatmentFeedback(SehatyBase, TimestampMixin):
    """A patient reporting whether a prescription/diagnosis/visit helped."""

    __tablename__ = "treatment_feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    clinic_patient_id: Mapped[int] = mapped_column(
        ForeignKey("clinic_patients.id", ondelete="CASCADE"), index=True
    )
    # The patient app user who left the feedback; keep the row if they're removed.
    author_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    # One of "prescription" | "diagnosis" | "appointment".
    target_type: Mapped[str] = mapped_column(String(24))
    target_id: Mapped[int] = mapped_column(Integer)
    outcome: Mapped[TreatmentOutcome] = mapped_column(
        Enum(TreatmentOutcome, name="treatment_outcome")
    )
    comment: Mapped[str | None] = mapped_column(String(1000), nullable=True)


class PracticeProfile(SehatyBase, TimestampMixin):
    """A doctor's letterhead for one location (they may have several)."""

    __tablename__ = "practice_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(160))  # e.g. "Cabinet Zerktouni"
    clinic_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    address: Mapped[str | None] = mapped_column(String(300), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    header_line: Mapped[str | None] = mapped_column(String(300), nullable=True)
    # Printed signature text; defaults to the doctor's name at the app layer.
    signature_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    signature_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Filigrane text, e.g. the clinic name.
    watermark_text: Mapped[str | None] = mapped_column(String(120), nullable=True)
    watermark_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_default: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false"), default=False
    )


class AuditLog(SehatyBase):
    """Immutable, append-only trail for sensitive actions (prescribe, dispense, accredit)."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(64))
    entity: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[int | None] = mapped_column(Integer)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    meta: Mapped[str | None] = mapped_column(String(1000))
