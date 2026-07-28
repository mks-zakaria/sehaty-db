"""doctor-written answers to patient questions

Revision ID: c8d9e0f1a2b3
Revises: b7c8d9e0f1a2
Create Date: 2026-07-28 22:30:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c8d9e0f1a2b3"
down_revision: str | None = "b7c8d9e0f1a2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_STATUS = postgresql.ENUM(
    "DRAFT", "PENDING", "PUBLISHED", "REJECTED", name="article_status", create_type=False
)


def upgrade() -> None:
    # Explicit create, then create_type=False on the column: attaching a plain
    # sa.Enum re-emits CREATE TYPE and fails on a type that now exists.
    _STATUS.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("locale", sa.String(length=8), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("slug", sa.String(length=320), nullable=False),
        sa.Column("summary", sa.String(length=500), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("specialty_slug", sa.String(length=64), nullable=True),
        sa.Column("status", _STATUS, nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_note", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_articles_slug"),
    )
    op.create_index("ix_articles_author", "articles", ["author_id"])
    op.create_index("ix_articles_author_id", "articles", ["author_id"])
    op.create_index("ix_articles_slug", "articles", ["slug"])
    op.create_index("ix_articles_specialty_slug", "articles", ["specialty_slug"])
    op.create_index("ix_articles_status_published", "articles", ["status", "published_at"])


def downgrade() -> None:
    op.drop_table("articles")
    _STATUS.drop(op.get_bind(), checkfirst=True)
