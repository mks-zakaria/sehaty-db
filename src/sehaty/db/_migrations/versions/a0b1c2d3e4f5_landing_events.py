"""public-landing analytics events

Revision ID: a0b1c2d3e4f5
Revises: f9a0b1c2d3e4
Create Date: 2026-07-27 00:00:00.000000+00:00
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a0b1c2d3e4f5"
down_revision: str | None = "f9a0b1c2d3e4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_EVENT_TYPES = (
    "PAGE_VIEW",
    "QR_SCAN",
    "CALL_CLICK",
    "WHATSAPP_CLICK",
    "DIRECTIONS_CLICK",
    "BOOK_CLICK",
)


def upgrade() -> None:
    op.create_table(
        "landing_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "doctor_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "type",
            sa.Enum(*_EVENT_TYPES, name="landing_event_type"),
            nullable=False,
        ),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        # Coarse source only ("qr", "google", "direct") — never a full referrer,
        # which can carry a search query and thus health data.
        sa.Column("source", sa.String(32), nullable=True),
    )
    op.create_index("ix_landing_events_doctor_id", "landing_events", ["doctor_id"])
    op.create_index("ix_landing_events_occurred_at", "landing_events", ["occurred_at"])
    # Serves the monthly per-doctor rollup, which is the only read path.
    op.create_index(
        "ix_landing_events_doctor_occurred",
        "landing_events",
        ["doctor_id", "occurred_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_landing_events_doctor_occurred", table_name="landing_events")
    op.drop_index("ix_landing_events_occurred_at", table_name="landing_events")
    op.drop_index("ix_landing_events_doctor_id", table_name="landing_events")
    op.drop_table("landing_events")
    sa.Enum(name="landing_event_type").drop(op.get_bind(), checkfirst=True)
