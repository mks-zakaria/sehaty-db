"""add doctor languages

Revision ID: a1b2c3d4e5f6
Revises: 0ba77772b5fa
Create Date: 2026-07-15 00:00:00.000000+00:00
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: str | None = '0ba77772b5fa'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Portable JSON column so spoken languages persist on both SQLite and Postgres.
    # Add with server_default '[]' to backfill existing rows, then drop the default:
    # Postgres `json` has no `=` operator, so a lingering server_default would break
    # alembic's autogenerate/`check` comparison. Final DB state matches the model
    # (no server_default; empty list is supplied Python-side via default=list).
    op.add_column(
        "doctor_profiles",
        sa.Column("languages", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
    )
    op.alter_column("doctor_profiles", "languages", server_default=None)


def downgrade() -> None:
    op.drop_column("doctor_profiles", "languages")
