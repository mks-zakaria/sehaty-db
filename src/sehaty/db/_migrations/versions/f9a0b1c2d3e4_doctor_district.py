"""doctor district (neighbourhood browse axis)

Revision ID: f9a0b1c2d3e4
Revises: e8f9a0b1c2d3
Create Date: 2026-07-27 00:00:00.000000+00:00
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f9a0b1c2d3e4"
down_revision: str | None = "e8f9a0b1c2d3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Nullable: existing doctors have no neighbourhood recorded, and the import
    # path fills it in going forward. Indexed because it is a directory filter,
    # not merely display text.
    op.add_column("doctor_profiles", sa.Column("district", sa.String(128), nullable=True))
    op.create_index("ix_doctor_profiles_district", "doctor_profiles", ["district"])


def downgrade() -> None:
    op.drop_index("ix_doctor_profiles_district", table_name="doctor_profiles")
    op.drop_column("doctor_profiles", "district")
