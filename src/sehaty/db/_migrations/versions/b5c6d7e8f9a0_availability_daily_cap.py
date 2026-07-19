"""availability daily cap: CAP exception kind + max_patients

Revision ID: b5c6d7e8f9a0
Revises: a4b5c6d7e8f9
Create Date: 2026-07-19 16:00:00.000000+00:00

A doctor can cap how many patients they accept on a given date. This adds the
``CAP`` value to the ``availability_exception_kind`` enum and a ``max_patients``
column that holds the cap (NULL for BLOCK/OPEN exceptions).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b5c6d7e8f9a0"
down_revision: str | None = "a4b5c6d7e8f9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Postgres has a real enum type; SQLite stores the column as VARCHAR.
    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TYPE availability_exception_kind ADD VALUE IF NOT EXISTS 'CAP'")
    op.add_column(
        "availability_exceptions",
        sa.Column("max_patients", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("availability_exceptions", "max_patients")
    # Postgres cannot drop enum values; CAP remains on the enum (harmless).