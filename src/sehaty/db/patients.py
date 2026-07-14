"""Doctor-owned patient register (clinic_patients).

A doctor/assistant keeps a register of ALL their patients: app users who booked
(user_id links the account) AND walk-in/phone patients with no app account
(user_id is NULL). Each row carries denormalised contact + demographic fields and
the assistant's running notes — the foundation for a patient-management grid.
"""

from sqlalchemy import (
    JSON,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from sehaty.db.base import SehatyBase, TimestampMixin


class ClinicPatient(SehatyBase, TimestampMixin):
    __tablename__ = "clinic_patients"
    __table_args__ = (
        # One register row per app patient per doctor. NULL user_ids (walk-ins) are
        # allowed to repeat under standard SQL NULL semantics on both Postgres and
        # SQLite — a plain UniqueConstraint is portable (partial unique is not).
        UniqueConstraint("doctor_id", "user_id", name="uq_clinic_patients_doctor_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # The owning doctor. Register disappears if the doctor account is deleted.
    doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    # Link to the app account when the patient uses the app; NULL for pure walk-ins.
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sex: Mapped[str | None] = mapped_column(String(16), nullable=True)
    birth_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Assistant's running notes on this patient.
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    # Free-form tags, e.g. ["chronic", "vip"]. Portable JSON so it persists on both
    # SQLite (tests) and Postgres (prod). No server_default: Postgres `json` has no
    # `=` operator, which would break alembic's server-default comparison.
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, default=list)
    no_show_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0"), default=0
    )
    # Who added the record (doctor or staff account); keep the row if they're removed.
    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
