"""doctor public contact, opening hours and insurance

Revision ID: e8f9a0b1c2d3
Revises: d7e8f9a0b1c2
Create Date: 2026-07-27 00:00:00.000000+00:00
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e8f9a0b1c2d3"
down_revision: str | None = "d7e8f9a0b1c2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Public cabinet contact numbers — nullable, no backfill possible.
    op.add_column("doctor_profiles", sa.Column("phone_fixe", sa.String(32), nullable=True))
    op.add_column("doctor_profiles", sa.Column("phone_mobile", sa.String(32), nullable=True))
    op.add_column("doctor_profiles", sa.Column("whatsapp", sa.String(32), nullable=True))

    # Portable JSON columns. Add with server_default '[]' so existing rows satisfy
    # NOT NULL, then drop the default: Postgres `json` has no `=` operator, so a
    # lingering server_default breaks alembic's autogenerate/`check` comparison.
    # Final DB state matches the model (no server_default; default=list Python-side).
    op.add_column(
        "doctor_profiles",
        sa.Column("opening_hours", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
    )
    op.alter_column("doctor_profiles", "opening_hours", server_default=None)

    op.add_column(
        "doctor_profiles",
        sa.Column("insurances", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
    )
    op.alter_column("doctor_profiles", "insurances", server_default=None)

    # Boolean keeps its server_default: unlike json, boolean compares cleanly under
    # alembic check, and the model declares the same default.
    op.add_column(
        "doctor_profiles",
        sa.Column(
            "tiers_payant", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
    )


def downgrade() -> None:
    op.drop_column("doctor_profiles", "tiers_payant")
    op.drop_column("doctor_profiles", "insurances")
    op.drop_column("doctor_profiles", "opening_hours")
    op.drop_column("doctor_profiles", "whatsapp")
    op.drop_column("doctor_profiles", "phone_mobile")
    op.drop_column("doctor_profiles", "phone_fixe")
