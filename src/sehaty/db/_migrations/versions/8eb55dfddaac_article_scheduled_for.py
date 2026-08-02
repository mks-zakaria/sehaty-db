"""article scheduled_for

When a finished draft should publish itself. Separate from `published_at`,
which records when it did: a DRAFT carrying a date here is scheduled, and a
DRAFT without one is merely unfinished. Only the first is ever touched by the
sweep, so nothing goes public because a job ran.

Indexed because the sweep queries it every few minutes and asks the same
question each time — which drafts are due.

Revision ID: 8eb55dfddaac
Revises: 1e47ca63ecda
Create Date: 2026-08-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8eb55dfddaac"
down_revision: str | None = "1e47ca63ecda"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "articles", sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index(
        op.f("ix_articles_scheduled_for"), "articles", ["scheduled_for"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_articles_scheduled_for"), table_name="articles")
    op.drop_column("articles", "scheduled_for")
