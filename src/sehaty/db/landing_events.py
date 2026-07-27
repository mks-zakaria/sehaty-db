"""Public-landing analytics: what a doctor's page actually does for them.

One row per meaningful interaction with a doctor's public page. This is the
evidence behind the upsell conversation — "your page had 340 views and 22 people
tapped Appeler last month" — so it has to exist from the first published page,
not be added once someone asks for a report.

Privacy: no IP address, no user agent, no cookie, no patient identity. A row
says *that* something happened to a doctor's page, never *who* did it. The page
is a health-adjacent surface, and the visitor is usually a patient looking for
that specialty; storing an identifier alongside a dermatologist's page view
would create health data about a person we have no relationship with.
"""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from sehaty.db.base import SehatyBase, utcnow


class LandingEventType(enum.StrEnum):
    # The page was rendered for a visitor.
    PAGE_VIEW = "PAGE_VIEW"
    # Arrived via the waiting-room QR (the `?src=qr` marker on the printed code).
    QR_SCAN = "QR_SCAN"
    # Tapped a call-to-action. These are the numbers that sell a subscription:
    # they are intent, not traffic.
    CALL_CLICK = "CALL_CLICK"
    WHATSAPP_CLICK = "WHATSAPP_CLICK"
    DIRECTIONS_CLICK = "DIRECTIONS_CLICK"
    BOOK_CLICK = "BOOK_CLICK"


class LandingEvent(SehatyBase):
    """One interaction with a doctor's public landing page."""

    __tablename__ = "landing_events"
    __table_args__ = (
        # The only query that matters: one doctor's events over a date range,
        # grouped by type. A composite index serves the monthly rollup directly.
        Index("ix_landing_events_doctor_occurred", "doctor_id", "occurred_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    type: Mapped[LandingEventType] = mapped_column(
        Enum(LandingEventType, name="landing_event_type")
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
    # Coarse traffic source only ("qr", "google", "direct", "whatsapp"). Never a
    # full referring URL, which can carry a search query — and a query typed
    # before landing on a specialist's page is health data.
    source: Mapped[str | None] = mapped_column(String(32), nullable=True)
