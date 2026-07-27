"""User + profile models. DoctorProfile carries the marketplace/geo fields."""

import enum
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import JSON, Boolean, DateTime, Enum, Float, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sehaty.db.base import SehatyBase, TimestampMixin


class UserRole(enum.StrEnum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"
    # A doctor's assistant/secretary: logs in to manage the doctor's schedule and
    # patient register (e.g. call patients to confirm appointments). Cannot prescribe.
    ASSISTANT = "ASSISTANT"
    # A pharmacy: logs in to look up a prescription by its code/QR and dispense
    # its items (decrementing stock). Cannot prescribe or manage patients.
    PHARMACY = "PHARMACY"


class ClaimStatus(enum.StrEnum):
    """Whether the doctor has taken ownership of their public page.

    Pages are published from public professional data before the doctor is ever
    contacted, so most start UNCLAIMED. That state is shown on the page itself
    with a "vous êtes ce médecin ?" banner and a removal link — publishing
    someone's professional listing is defensible, publishing it with no way to
    correct or remove it is not.
    """

    # Built by us from public data; the doctor has not engaged.
    UNCLAIMED = "UNCLAIMED"
    # The doctor asked for it and we handed it over, but identity is unproven.
    CLAIMED = "CLAIMED"
    # Identity checked against the licence — the only state that shows a badge.
    VERIFIED = "VERIFIED"
    # The doctor asked to be delisted. Kept as a tombstone so a later import
    # cannot silently republish them.
    REMOVAL_REQUESTED = "REMOVAL_REQUESTED"


class ProfileSource(enum.StrEnum):
    """How the profile got here — needed to honour removals and audit imports."""

    MANUAL = "MANUAL"
    IMPORT = "IMPORT"
    SELF_SIGNUP = "SELF_SIGNUP"


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
    # Neighbourhood within the city, as displayed ("Maârif", "Gauthier"). Stored
    # separately from the free-text ``address`` because it is a browse axis: it
    # drives /{city}/{district}/{specialty} pages and the searches people
    # actually type here ("dentiste maarif"). Indexed for the directory filter.
    district: Mapped[str | None] = mapped_column(String(128), index=True)
    # PostGIS point (lon/lat, WGS84) for nearest-doctor search. The GIST index is
    # added explicitly in a later migration (spatial_index=False avoids GeoAlchemy2's
    # auto-index fighting Alembic on up/down cycles).
    geopoint: Mapped[object | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=False), nullable=True
    )
    # Clinic's IANA timezone (e.g. "Africa/Casablanca"). Availability wall-clock
    # times are interpreted in this zone so slots generate in local time rather than
    # being wrongly treated as UTC. server_default backfills existing rows; a plain
    # String server_default compares fine on Postgres (unlike JSON), so the model
    # keeps the same server_default to stay clean under alembic check.
    timezone: Mapped[str] = mapped_column(
        String(64), nullable=False, server_default=text("'Africa/Casablanca'")
    )
    consultation_fee: Mapped[float | None] = mapped_column(Float)
    # --- Public cabinet contact. Distinct from ``User.phone``, which is the login
    # identity (unique, private). These are the numbers printed on the public
    # landing page: the patient calls the cabinet, not the doctor's account.
    # ``whatsapp`` is stored separately because it is frequently a different line
    # from the fixed one and it drives the page's primary CTA.
    phone_fixe: Mapped[str | None] = mapped_column(String(32))
    phone_mobile: Mapped[str | None] = mapped_column(String(32))
    whatsapp: Mapped[str | None] = mapped_column(String(32))
    # Weekly opening hours, one entry per open weekday:
    #   [{"weekday": 0, "ranges": [["09:00", "12:30"], ["15:00", "19:00"]]}, ...]
    # ``weekday`` follows the same convention as ``Availability.weekday``
    # (0=Monday .. 6=Sunday); a missing weekday (or empty ``ranges``) means closed.
    # Two ranges is the norm here — Moroccan cabinets almost always break at midday.
    # Structured rather than free text because it also feeds the page's
    # openingHoursSpecification JSON-LD and the doctor's Google listing.
    # Portable JSON so it persists on both SQLite (tests) and Postgres (prod);
    # see ``languages`` for why there is no server_default on the model.
    opening_hours: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    # Accepted third-party payers, as slugs: ["cnss", "cnops", "amo", "saham", ...].
    # Empty list = unspecified. One of the first things a patient checks.
    insurances: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    # Whether the cabinet advances the insurer's share (tiers payant) rather than
    # making the patient pay in full and claim it back.
    tiers_payant: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false"), default=False
    )
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
    # Ownership of the public page, distinct from ``verification_status`` (which
    # gates whether the page is publicly visible at all).
    claim_status: Mapped[ClaimStatus] = mapped_column(
        Enum(ClaimStatus, name="claim_status"),
        nullable=False,
        server_default=text("'UNCLAIMED'"),
        default=ClaimStatus.UNCLAIMED,
        index=True,
    )
    source: Mapped[ProfileSource] = mapped_column(
        Enum(ProfileSource, name="profile_source"),
        nullable=False,
        server_default=text("'MANUAL'"),
        default=ProfileSource.MANUAL,
    )
    # When a delisting was requested, so the honouring of it is auditable.
    removal_requested_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    referral_code: Mapped[str | None] = mapped_column(String(32), unique=True, index=True)
    # Secretariat account for a practice: manage calendar, cannot prescribe.
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="doctor_profile")
