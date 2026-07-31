"""illustrations on an article, and readers voting on whether it helped

Revision ID: 4d5e6f7a8b9c
Revises: 3c4d5e6f7a8b
Create Date: 2026-07-31 01:00:00.000000+00:00

Two additions, both about trust rather than features.

`articles.images` holds illustrations in two stages: a brief describing what a
diagram should show, and later the sourced image. A draft arrives with briefs and
no URLs, because a writer can say what a diagram should show and must not invent
the diagram — a reader trusts a picture of an artery far more readily than a
sentence about one, and cannot check it.

`article_votes` records whether an article helped the person who read it. The
point is not a score: an article with many readers and a falling helpful rate is
one to send back to a doctor. `voter_key` is a salted hash, never an IP and never
an account — a vote on an article about depression must not become a record that
a particular person read about depression.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4d5e6f7a8b9c"
down_revision: str | None = "3c4d5e6f7a8b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Server default only to fill existing rows; dropped so the schema matches
    # the model, which declares none.
    op.add_column(
        "articles",
        sa.Column("images", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
    )
    op.alter_column("articles", "images", server_default=None)

    op.create_table(
        "article_votes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "article_id",
            sa.Integer(),
            sa.ForeignKey("articles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("voter_key", sa.String(length=64), nullable=False),
        sa.Column("helpful", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("article_id", "voter_key", name="uq_article_vote_once"),
    )
    op.create_index("ix_article_votes_article", "article_votes", ["article_id"])


def downgrade() -> None:
    op.drop_index("ix_article_votes_article", table_name="article_votes")
    op.drop_table("article_votes")
    op.drop_column("articles", "images")
