"""appointment no-overlap exclusion constraint

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-07-15 06:00:00.000000+00:00
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c9d0e1f2a3b4"
down_revision: str | None = "b8c9d0e1f2a3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # DB-level defence against booking races. App code does check-then-insert,
    # which is not atomic under concurrency; this makes two overlapping ACTIVE
    # appointments for the same doctor impossible at the storage layer.
    #
    # Postgres-only. SQLite has no EXCLUDE constraint, but the SQLite test suite
    # builds tables straight from the ORM metadata (which deliberately does NOT
    # carry this constraint), so this migration simply no-ops there. Guard on the
    # dialect so the raw SQL only runs on Postgres.
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    # btree_gist lets a plain-equality column (doctor_id) share a single GiST
    # index with a range/overlap operator (tstzrange && tstzrange). Without it,
    # GiST cannot index the `doctor_id WITH =` element.
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    # EXCLUDE: reject any row whose doctor_id equals AND whose [start_at, end_at)
    # interval overlaps an existing row's. The partial WHERE limits the constraint
    # to ACTIVE statuses (REQUESTED / CONFIRMED), so a CANCELLED / NO_SHOW /
    # COMPLETED slot leaves its time free to be re-booked.
    op.execute(
        """
        ALTER TABLE appointments
        ADD CONSTRAINT appointments_no_overlap
        EXCLUDE USING gist (
            doctor_id WITH =,
            tstzrange(start_at, end_at) WITH &&
        )
        WHERE (status IN ('REQUESTED', 'CONFIRMED'))
        """
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    # Drop only the constraint; leave btree_gist installed (other objects may use
    # it, and dropping an extension is not something a schema rollback should own).
    op.execute("ALTER TABLE appointments DROP CONSTRAINT IF EXISTS appointments_no_overlap")
