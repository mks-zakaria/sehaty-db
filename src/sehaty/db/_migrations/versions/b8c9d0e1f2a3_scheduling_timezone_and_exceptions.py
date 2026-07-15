"""scheduling timezone and availability exceptions

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-07-15 05:00:00.000000+00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b8c9d0e1f2a3"
down_revision: str | None = "a7b8c9d0e1f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1) Per-doctor clinic timezone so availability wall-clock times generate slots
    #    in local time instead of being wrongly treated as UTC. server_default
    #    backfills existing rows; a plain String default compares fine under alembic
    #    check (Postgres has an `=` operator for text), so the model keeps the same
    #    server_default and no follow-up alter is needed.
    op.add_column(
        "doctor_profiles",
        sa.Column(
            "timezone",
            sa.String(length=64),
            nullable=False,
            server_default=sa.text("'Africa/Casablanca'"),
        ),
    )

    # 2) Date-specific overrides of the recurring weekly availability. The
    #    `availability_exception_kind` enum type is created by sa.Enum inside
    #    create_table (Postgres); on SQLite it degrades to a CHECK/varchar.
    op.create_table(
        "availability_exceptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("doctor_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column(
            "kind",
            sa.Enum("BLOCK", "OPEN", name="availability_exception_kind"),
            nullable=False,
        ),
        sa.Column("start_time", sa.Time(), nullable=True),
        sa.Column("end_time", sa.Time(), nullable=True),
        sa.Column("slot_minutes", sa.Integer(), nullable=True),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["doctor_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_availability_exceptions_doctor_id"),
        "availability_exceptions",
        ["doctor_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_availability_exceptions_date"),
        "availability_exceptions",
        ["date"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_availability_exceptions_date"), table_name="availability_exceptions"
    )
    op.drop_index(
        op.f("ix_availability_exceptions_doctor_id"), table_name="availability_exceptions"
    )
    op.drop_table("availability_exceptions")
    # sa.Enum-created type must be dropped explicitly on Postgres; no-op on SQLite.
    op.execute("DROP TYPE IF EXISTS availability_exception_kind")

    op.drop_column("doctor_profiles", "timezone")
