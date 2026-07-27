"""doctor claim status, profile source and removal request

Revision ID: b1c2d3e4f5a6
Revises: a0b1c2d3e4f5
Create Date: 2026-07-27 00:00:00.000000+00:00
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "b1c2d3e4f5a6"
down_revision: str | None = "a0b1c2d3e4f5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_CLAIM_STATUSES = ("UNCLAIMED", "CLAIMED", "VERIFIED", "REMOVAL_REQUESTED")
_PROFILE_SOURCES = ("MANUAL", "IMPORT", "SELF_SIGNUP")

# Postgres enum types are created explicitly below, so every column reference
# must use `create_type=False`. A plain `sa.Enum` re-emits CREATE TYPE when it is
# attached to a column, which collides with the explicit create and aborts the
# migration with "type ... already exists".



def upgrade() -> None:
    bind = op.get_bind()
    sa.Enum(*_CLAIM_STATUSES, name="claim_status").create(bind, checkfirst=True)
    sa.Enum(*_PROFILE_SOURCES, name="profile_source").create(bind, checkfirst=True)

    claim_status = postgresql.ENUM(*_CLAIM_STATUSES, name="claim_status", create_type=False)
    profile_source = postgresql.ENUM(
        *_PROFILE_SOURCES, name="profile_source", create_type=False
    )

    # Existing rows predate the import pipeline, so they were entered by hand and
    # belong to doctors we already dealt with directly: MANUAL, and treated as
    # CLAIMED rather than UNCLAIMED so they do not suddenly show a claim banner.
    op.add_column(
        "doctor_profiles",
        sa.Column(
            "claim_status",
            claim_status,
            nullable=False,
            server_default=sa.text("'CLAIMED'"),
        ),
    )
    op.alter_column(
        "doctor_profiles", "claim_status", server_default=sa.text("'UNCLAIMED'")
    )
    op.add_column(
        "doctor_profiles",
        sa.Column(
            "source", profile_source, nullable=False, server_default=sa.text("'MANUAL'")
        ),
    )
    op.add_column(
        "doctor_profiles",
        sa.Column("removal_requested_at", sa.DateTime(timezone=True), nullable=True),
    )
    # Import and moderation both scan by claim state.
    op.create_index(
        "ix_doctor_profiles_claim_status", "doctor_profiles", ["claim_status"]
    )


def downgrade() -> None:
    op.drop_index("ix_doctor_profiles_claim_status", table_name="doctor_profiles")
    op.drop_column("doctor_profiles", "removal_requested_at")
    op.drop_column("doctor_profiles", "source")
    op.drop_column("doctor_profiles", "claim_status")
    bind = op.get_bind()
    sa.Enum(name="profile_source").drop(bind, checkfirst=True)
    sa.Enum(name="claim_status").drop(bind, checkfirst=True)
