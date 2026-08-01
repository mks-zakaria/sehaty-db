"""article topic key for language pairs

Groups the articles that answer the same question in different languages, so a
reader on the French version can be handed the Arabic one.

Nullable and unindexed-by-uniqueness on purpose. An article without a
counterpart is the normal case, and two articles sharing a key is exactly what
the column is for — the pair is found by equality, not by a pointer from one to
the other. Neither version is the original: each is written from the same
passages in its own language.

Revision ID: 1e47ca63ecda
Revises: 5e6f7a8b9c0d
Create Date: 2026-08-01 12:48:53.512870+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1e47ca63ecda"
down_revision: str | None = "5e6f7a8b9c0d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("articles", sa.Column("topic_key", sa.String(length=120), nullable=True))
    op.create_index(op.f("ix_articles_topic_key"), "articles", ["topic_key"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_articles_topic_key"), table_name="articles")
    op.drop_column("articles", "topic_key")
