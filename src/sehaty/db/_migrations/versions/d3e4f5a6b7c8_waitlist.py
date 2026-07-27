"""per-doctor waitlist for freed slots

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-07-27 00:00:00.000000+00:00
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "d3e4f5a6b7c8"
down_revision: str | None = "c2d3e4f5a6b7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_STATUSES = ("WAITING", "OFFERED", "ACCEPTED", "PASSED", "CANCELLED")

# Postgres enum types are created explicitly below, so every column reference
# must use `create_type=False`. A plain `sa.Enum` re-emits CREATE TYPE when it is
# attached to a column, which collides with the explicit create and aborts the
# migration with "type ... already exists".



def upgrade() -> None:
    sa.Enum(*_STATUSES, name="waitlist_status").create(op.get_bind(), checkfirst=True)
    status = postgresql.ENUM(*_STATUSES, name="waitlist_status", create_type=False)

    op.create_table(
        "waitlist_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "doctor_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "patient_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", status, nullable=False),
        sa.Column("earliest_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("latest_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "offered_appointment_id",
            sa.Integer(),
            sa.ForeignKey("appointments.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("offered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("note", sa.String(300), nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        # Matches TimestampMixin exactly: created_at only, defaulted by the
        # database. A hand-written column that drifts from the mixin fails
        # `alembic check`.
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        # Asking twice must not double a patient's odds or send two offers.
        sa.UniqueConstraint("doctor_id", "patient_id", name="uq_waitlist_doctor_patient"),
    )
    op.create_index("ix_waitlist_entries_doctor_id", "waitlist_entries", ["doctor_id"])
    op.create_index("ix_waitlist_entries_patient_id", "waitlist_entries", ["patient_id"])
    # Serves the offer query: this doctor's waiting entries, oldest first.
    op.create_index(
        "ix_waitlist_doctor_status_created",
        "waitlist_entries",
        ["doctor_id", "status", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_waitlist_doctor_status_created", table_name="waitlist_entries")
    op.drop_index("ix_waitlist_entries_patient_id", table_name="waitlist_entries")
    op.drop_index("ix_waitlist_entries_doctor_id", table_name="waitlist_entries")
    op.drop_table("waitlist_entries")
    sa.Enum(name="waitlist_status").drop(op.get_bind(), checkfirst=True)
