"""add PHARMACY to the user_role enum

Revision ID: d1a2c3b4e5f6
Revises: cab1e70c0de1
Create Date: 2026-07-19 12:00:00.000000+00:00

Pharmacies log in to look up a prescription and dispense it. They are ordinary
``users`` rows with the new ``PHARMACY`` role; the pharmacy tables
(``pharmacy_stock`` / ``dispenses`` / ``dispense_items``) already exist.
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d1a2c3b4e5f6"
down_revision: str | None = "cab1e70c0de1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Postgres has a real enum type; SQLite stores the column as VARCHAR so no
    # type change is needed there.
    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'PHARMACY'")


def downgrade() -> None:
    # Postgres cannot drop enum values; PHARMACY remains on user_role (harmless).
    pass
