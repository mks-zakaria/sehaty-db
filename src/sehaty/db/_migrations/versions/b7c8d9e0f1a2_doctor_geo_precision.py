"""how far to trust a doctor's coordinates

Revision ID: b7c8d9e0f1a2
Revises: f0a1b2c3d4e5
Create Date: 2026-07-28 09:30:00.000000+00:00

Imported pages are geocoded from written addresses, and a Moroccan cabinet
address is a lotissement-and-block reference no map database holds. The point
that comes back is the quartier, not the door — good enough to place a doctor
in "près de chez moi", not good enough to navigate to.

Existing rows are backfilled to EXACT rather than left NULL: every coordinate
predating this column came from a doctor's own profile edit or the demo seed,
where the point really is the cabinet. Marking those APPROXIMATE would be a
downgrade of data that is fine.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b7c8d9e0f1a2"
down_revision: str | None = "f0a1b2c3d4e5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_PRECISION = postgresql.ENUM(
    "EXACT", "APPROXIMATE", name="geo_precision", create_type=False
)


def upgrade() -> None:
    # Explicit create, then create_type=False on the column: attaching a plain
    # sa.Enum to the column re-emits CREATE TYPE and fails on a type that now
    # exists.
    _PRECISION.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "doctor_profiles",
        sa.Column("geo_precision", _PRECISION, nullable=True),
    )
    # Backfill before anything reads it, so no window exists where a real
    # coordinate looks like one of unknown provenance.
    op.execute(
        "UPDATE doctor_profiles SET geo_precision = 'EXACT' WHERE geopoint IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_column("doctor_profiles", "geo_precision")
    _PRECISION.drop(op.get_bind(), checkfirst=True)
