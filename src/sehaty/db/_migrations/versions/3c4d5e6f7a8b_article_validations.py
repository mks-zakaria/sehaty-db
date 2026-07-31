"""articles the platform writes and doctors sign

Revision ID: 3c4d5e6f7a8b
Revises: 2b3c4d5e6f7a
Create Date: 2026-07-30 07:00:00.000000+00:00

Waiting for physicians to write does not fill a directory — it produces a few
answers in the specialties that happen to have enthusiastic doctors and nothing
in the rest. So the platform writes from the medical literature and asks doctors
to check the result, which is a five-minute favour rather than homework.

Three changes, all additive:

* `articles.author_id` becomes nullable — a platform-written article has no
  single author to attribute an opinion to. Every existing row keeps its author.
* `articles.sources` records what it was drawn from. An article about a disease
  that cites nothing is indistinguishable from one a machine invented.
* `article_validations` records which doctors put their name to it, and whether
  they agreed, corrected or added. That endorsement is what the article's
  standing rests on, and the link back to the doctor's page is what makes signing
  worth their time.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "3c4d5e6f7a8b"
down_revision: str | None = "2b3c4d5e6f7a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# `create_type=False`: the type is created once, explicitly, in upgrade(). Left
# to itself `op.create_table` emits its own CREATE TYPE for the column and the
# migration dies on a duplicate object it created a line earlier.
_VERDICT = postgresql.ENUM(
    "VALIDATED", "RECTIFIED", "ENRICHED", name="validation_verdict", create_type=False
)


def upgrade() -> None:
    op.alter_column("articles", "author_id", existing_type=sa.Integer(), nullable=True)

    # Server default only to fill the rows that already exist; dropped again so
    # the schema matches the model, which declares none.
    op.add_column(
        "articles",
        sa.Column("sources", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
    )
    op.alter_column("articles", "sources", server_default=None)

    _VERDICT.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "article_validations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "article_id",
            sa.Integer(),
            sa.ForeignKey("articles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "doctor_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("verdict", _VERDICT, nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        # One endorsement per doctor per article: five validations must mean five
        # doctors, not one doctor pressing the button five times.
        sa.UniqueConstraint("article_id", "doctor_id", name="uq_article_validation_once"),
    )
    op.create_index("ix_article_validations_article", "article_validations", ["article_id"])
    op.create_index("ix_article_validations_doctor", "article_validations", ["doctor_id"])


def downgrade() -> None:
    op.drop_index("ix_article_validations_doctor", table_name="article_validations")
    op.drop_index("ix_article_validations_article", table_name="article_validations")
    op.drop_table("article_validations")
    _VERDICT.drop(op.get_bind(), checkfirst=True)
    op.drop_column("articles", "sources")
    # Rows written without an author cannot be given one, so they are removed
    # rather than blocking the downgrade on a NOT NULL that cannot be satisfied.
    op.execute("DELETE FROM articles WHERE author_id IS NULL")
    op.alter_column("articles", "author_id", existing_type=sa.Integer(), nullable=False)
