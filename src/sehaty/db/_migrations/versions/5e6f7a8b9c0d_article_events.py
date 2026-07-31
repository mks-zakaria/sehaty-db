"""what readers actually do with an article

Revision ID: 5e6f7a8b9c0d
Revises: 4d5e6f7a8b9c
Create Date: 2026-07-31 14:00:00.000000+00:00

Topic selection was running on published disease prevalence, which is a proxy for
demand and a poor one: someone with cirrhosis may never search for it, while
someone frightened about their liver searches every week. Only our own traffic
can settle which articles are worth writing more of.

`source` records the channel a reader arrived by, so "ranks on Google" and
"travels on WhatsApp" stop being the same number — they need different articles.

DOCTOR_CLICK is the commercially important row: it measures an article sending a
reader to a doctor's page, which is the entire consideration offered to a doctor
for signing one.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5e6f7a8b9c0d"
down_revision: str | None = "4d5e6f7a8b9c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# create_type=False: the type is created once below, explicitly. Left to itself
# create_table emits its own CREATE TYPE and the migration dies on a duplicate.
_EVENT = postgresql.ENUM(
    "PAGE_VIEW", "DOCTOR_CLICK", name="article_event_type", create_type=False
)


def upgrade() -> None:
    _EVENT.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "article_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "article_id",
            sa.Integer(),
            sa.ForeignKey("articles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", _EVENT, nullable=False),
        # SET NULL rather than CASCADE: a doctor leaving must not erase the
        # evidence that articles were sending readers somewhere.
        sa.Column(
            "doctor_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # No server default: the model stamps this in Python (`default=utcnow`),
        # and a default declared on only one side is schema drift.
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=True),
    )
    # Name matches what `index=True` on the column generates.
    op.create_index("ix_article_events_article_id", "article_events", ["article_id"])
    op.create_index("ix_article_events_occurred_at", "article_events", ["occurred_at"])
    op.create_index(
        "ix_article_events_article_occurred", "article_events", ["article_id", "occurred_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_article_events_article_occurred", table_name="article_events")
    op.drop_index("ix_article_events_occurred_at", table_name="article_events")
    op.drop_index("ix_article_events_article_id", table_name="article_events")
    op.drop_table("article_events")
    _EVENT.drop(op.get_bind(), checkfirst=True)
