"""The hand switch for one doctor's booking engine.

There are two different reasons a cabinet takes no appointments online, and until
this table there was only one: whether they had paid. The other is that they do
not want an agenda — walk-ins only, or a secretary away for the month. Expressing
that by cancelling a subscription would misstate the books and switch off
everything else the doctor bought, so it gets its own record.

**Why a table and not a column on `doctor_profiles`.** Entitlement is resolved on
nearly every read path — public slots, booking, the waitlist, the payment board —
and its tests run on throwaway SQLite engines. `doctor_profiles` carries a
PostGIS geography column that SQLite cannot compile, so putting the switch there
would force every one of those fixtures to hand-write a stand-in table, and every
future one to discover the same thing. A small single-purpose table keeps the
service's dependencies buildable anywhere.

`disabled_at` NULL means the agenda is open — the row survives re-activation so
`note` ("walk-ins only") is still there the next time someone asks why.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from sehaty.db.base import SehatyBase, TimestampMixin


class DoctorBookingSwitch(SehatyBase, TimestampMixin):
    """Whether staff have switched this doctor's agenda off by hand."""

    __tablename__ = "doctor_booking_switches"

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    # When it was switched off. NULL = open, and the row is kept so the note
    # outlives a re-activation.
    disabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Why, in the operator's words. Shown next to the switch so the next person
    # to visit this cabinet does not undo a decision the doctor made.
    note: Mapped[str | None] = mapped_column(String(200), nullable=True)
