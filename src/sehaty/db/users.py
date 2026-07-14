"""User + profile models. DoctorProfile carries the marketplace/geo fields."""

import enum
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import JSON, Boolean, DateTime, Enum, Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sehaty.db.base import SehatyBase, TimestampMixin


class UserRole(enum.StrEnum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"


class VerificationStatus(enum.StrEnum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class User(SehatyBase, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Explicit consent to health-data processing (Law 09-08).
    consented_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    patient_profile: Mapped["PatientProfile"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    doctor_profile: Mapped["DoctorProfile"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class PatientProfile(SehatyBase):
    __tablename__ = "patient_profiles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    full_name: Mapped[str] = mapped_column(String(255))
    national_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    city: Mapped[str | None] = mapped_column(String(128))

    user: Mapped["User"] = relationship(back_populates="patient_profile")


class DoctorProfile(SehatyBase):
    __tablename__ = "doctor_profiles"
    __table_args__ = (
        # GIST spatial index for nearest-doctor / radius search on the geography point.
        Index("idx_doctor_profiles_geopoint", "geopoint", postgresql_using="gist"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    full_name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    license_no: Mapped[str] = mapped_column(String(64), unique=True)
    bio: Mapped[str | None] = mapped_column(String(2000))
    photo_url: Mapped[str | None] = mapped_column(String(512))
    address: Mapped[str | None] = mapped_column(String(512))
    city: Mapped[str | None] = mapped_column(String(128), index=True)
    # PostGIS point (lon/lat, WGS84) for nearest-doctor search. The GIST index is
    # added explicitly in a later migration (spatial_index=False avoids GeoAlchemy2's
    # auto-index fighting Alembic on up/down cycles).
    geopoint: Mapped[object | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=False), nullable=True
    )
    consultation_fee: Mapped[float | None] = mapped_column(Float)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, name="verification_status"),
        default=VerificationStatus.PENDING,
    )
    # Spoken languages (ar/fr/en) shown on the public landing. Portable JSON so it
    # persists on both SQLite (tests) and Postgres (prod). Empty list = unspecified.
    # No server_default on the model: Postgres `json` has no `=` operator, which breaks
    # alembic's server-default comparison. The migration backfills existing rows with
    # '[]' then drops the server default, so the DB matches this (default=list) model.
    languages: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    referral_code: Mapped[str | None] = mapped_column(String(32), unique=True, index=True)
    # Secretariat account for a practice: manage calendar, cannot prescribe.
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="doctor_profile")
