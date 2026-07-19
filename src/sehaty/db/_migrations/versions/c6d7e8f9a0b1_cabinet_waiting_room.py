"""cabinet waiting-room count + doctor alert threshold

Revision ID: c6d7e8f9a0b1
Revises: b5c6d7e8f9a0
Create Date: 2026-07-19 17:00:00.000000+00:00

The secretary maintains ``waiting_room_count`` (people physically waiting); the
doctor sets ``waiting_alert_threshold`` and is notified once the count reaches it
while they are not online at the cabinet.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c6d7e8f9a0b1"
down_revision: str | None = "b5c6d7e8f9a0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "cabinets",
        sa.Column(
            "waiting_room_count",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )
    op.add_column(
        "cabinets",
        sa.Column("waiting_alert_threshold", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("cabinets", "waiting_alert_threshold")
    op.drop_column("cabinets", "waiting_room_count")
