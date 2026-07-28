"""separate "publicly listed" from "we checked the licence"

Revision ID: d9e0f1a2b3c4
Revises: c8d9e0f1a2b3
Create Date: 2026-07-28 23:10:00.000000+00:00

Adding the enum value only. Postgres will not let a value added by ALTER TYPE
be *used* in the same transaction, so the backfill that actually moves rows onto
it lives in the next migration.
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d9e0f1a2b3c4"
down_revision: str | None = "c8d9e0f1a2b3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Postgres refuses to *use* an enum value added in the same transaction, and
    # alembic runs the whole upgrade in one. Committing here lets the backfill
    # migration that follows reference it.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE verification_status ADD VALUE IF NOT EXISTS 'LISTED'")


def downgrade() -> None:
    # Postgres cannot drop a single enum value. Leaving it is harmless: nothing
    # reads it once the backfill above is reverted.
    pass
