"""Per-doctor landing-page configuration.

An orthodontist's page should not read like a psychiatrist's. What a patient
needs to decide differs by specialty — a dentist is chosen on acts and prices, a
psychiatrist on discretion and whether teleconsultation exists, a gynaecologist
often on whether the practitioner is a woman. A single generic template serves
all of them badly.

**Templates are code; this table is configuration.** A template is a named
bundle of sections, accent and copy that lives in the landing app. Storing the
key rather than the markup means an eleventh look is a deploy, not a migration,
and no JSX ever ends up in Postgres.

``template`` is deliberately nullable: NULL means "use the default for my
specialty", which is what almost every doctor gets and never has to think about.
A value is an explicit override.

Commercially this is the upsell. The specialty template is free — a page that
suits the practice makes the whole directory better, and free pages are what
keep the city listings dense. What is paid is the doctor's *own* content on top:
their acts and prices, their equipment, their FAQ, their colour, their ordering.
``is_personalized`` is that flag, and it is the thing a subscription buys.
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column

from sehaty.db.base import SehatyBase, TimestampMixin


class DoctorLanding(SehatyBase, TimestampMixin):
    """One doctor's public-page configuration."""

    __tablename__ = "doctor_landings"

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    # Template key resolved by the landing app ("dentistry", "psychiatry", ...).
    # NULL = fall back to the doctor's primary specialty, then to "general".
    template: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # Brand accent as a hex string, e.g. "#2b73b3". Part of the paid tier: it is
    # the change a doctor notices first and asks for most.
    accent: Mapped[str | None] = mapped_column(String(9), nullable=True)
    # Ordered section keys overriding the template's default order. Empty list =
    # use the template's own order, which is the case for nearly everyone.
    section_order: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    # The acts this doctor performs: [{"label": "Détartrage", "price": 300}, ...].
    # `price` is optional — plenty of doctors will not publish one, and an
    # invented figure on a public page is worse than no figure.
    services: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    # Free-text equipment the cabinet has ("Radiographie panoramique"). A real
    # differentiator for dentists, ophthalmologists and cardiologists.
    equipment: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    # [{"q": "...", "a": "..."}] — also feeds FAQPage structured data.
    faq: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    # One line under the doctor's name, in their own words.
    tagline: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # False = the free, specialty-default page. True = the doctor is paying for
    # their own content and styling.
    is_personalized: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false"), default=False
    )
    personalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
