"""Medical specialties catalogue + doctor↔specialty association."""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from sehaty.db.base import SehatyBase


class Specialty(SehatyBase):
    __tablename__ = "specialties"

    id: Mapped[int] = mapped_column(primary_key=True)
    # e.g. "generalist", "gastroenterology", "optician"
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name_en: Mapped[str] = mapped_column(String(128))
    name_fr: Mapped[str] = mapped_column(String(128))
    name_ar: Mapped[str] = mapped_column(String(128))
    # Moroccan Arabic (darija) label; NULL falls back to ``name_ar`` in the UI.
    name_ary: Mapped[str | None] = mapped_column(String(128), nullable=True)


class DoctorSpecialty(SehatyBase):
    __tablename__ = "doctor_specialties"

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    specialty_id: Mapped[int] = mapped_column(
        ForeignKey("specialties.id", ondelete="CASCADE"), primary_key=True
    )
