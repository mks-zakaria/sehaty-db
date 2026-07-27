"""per-doctor landing page configuration

Revision ID: f0a1b2c3d4e5
Revises: d3e4f5a6b7c8
Create Date: 2026-07-28 00:00:00.000000+00:00
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f0a1b2c3d4e5"
down_revision: str | None = "d3e4f5a6b7c8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "doctor_landings",
        sa.Column(
            "doctor_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        # NULL = derive from the doctor's specialty; a value is an override.
        sa.Column("template", sa.String(64), nullable=True),
        sa.Column("accent", sa.String(9), nullable=True),
        # JSON columns land with a server_default so existing rows satisfy NOT
        # NULL, then drop it: Postgres `json` has no `=` operator, so a lingering
        # default breaks `alembic check`. Mirrors `languages` on doctor_profiles.
        sa.Column("section_order", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("services", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("equipment", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("faq", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("tagline", sa.String(200), nullable=True),
        sa.Column(
            "is_personalized", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column("personalized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    for column in ("section_order", "services", "equipment", "faq"):
        op.alter_column("doctor_landings", column, server_default=None)


def downgrade() -> None:
    op.drop_table("doctor_landings")
