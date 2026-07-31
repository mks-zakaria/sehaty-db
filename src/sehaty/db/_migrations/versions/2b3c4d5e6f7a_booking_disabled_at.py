"""a hand switch for one doctor's booking engine

Revision ID: 2b3c4d5e6f7a
Revises: 1a2b3c4d5e6f
Create Date: 2026-07-30 06:00:00.000000+00:00

Whether a cabinet takes appointments online was, until now, entirely a
consequence of whether they had paid. That conflates two different states: a
doctor who has not paid, and a doctor who does not want an agenda — takes
walk-ins only, or whose secretary is away for a month.

No row means "whatever the subscription says", which is every doctor today, so
applying this changes nothing for anyone. A row with `disabled_at` set closes the
agenda regardless of billing. There is deliberately no way to express the
opposite: entitlement stays the money truth, so an expired subscription still
closes the agenda by itself.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2b3c4d5e6f7a"
down_revision: str | None = "1a2b3c4d5e6f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "doctor_booking_switches",
        sa.Column(
            "doctor_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        # NULL = open. The row outlives a re-activation so the note survives.
        sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("note", sa.String(length=200), nullable=True),
        # Matches TimestampMixin: created_at only, NOT NULL, defaulted in the DB.
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("doctor_booking_switches")
