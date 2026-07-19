"""cabinets, cabinet sessions, and the appointment consultation record

Revision ID: cab1e70c0de1
Revises: f2e589ba0da9
Create Date: 2026-07-19 00:00:00.000000+00:00

Adds the cabinet (practice room) + cabinet-session (open shift / "doctor online")
model, links each appointment to the session that handled it, and extends
``appointments`` with the consultation record the doctor fills in at the desk
(real start/finish times + chief complaint, symptoms, vitals, exam notes). Also
adds the ``CHECKED_IN`` and ``IN_PROGRESS`` appointment statuses for the
secretary-check-in → consultation flow.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cab1e70c0de1"
down_revision: str | None = "f2e589ba0da9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# New appointment_status enum values, in flow order after CONFIRMED.
_NEW_STATUSES = ("CHECKED_IN", "IN_PROGRESS")


def upgrade() -> None:
    # A cabinet: one solo doctor's practice room, staffed by their secretaries.
    op.create_table(
        "cabinets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_doctor_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["owner_doctor_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_cabinets_owner_doctor_id"), "cabinets", ["owner_doctor_id"], unique=False
    )

    # A cabinet session: one open shift worked by the owner or a substitute doctor.
    op.create_table(
        "cabinet_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cabinet_id", sa.Integer(), nullable=False),
        sa.Column("acting_doctor_id", sa.Integer(), nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_open", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["cabinet_id"], ["cabinets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["acting_doctor_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_cabinet_sessions_cabinet_id"), "cabinet_sessions", ["cabinet_id"], unique=False
    )
    op.create_index(
        op.f("ix_cabinet_sessions_acting_doctor_id"),
        "cabinet_sessions",
        ["acting_doctor_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_cabinet_sessions_opened_at"), "cabinet_sessions", ["opened_at"], unique=False
    )
    op.create_index(
        op.f("ix_cabinet_sessions_is_open"), "cabinet_sessions", ["is_open"], unique=False
    )

    # New appointment_status enum values (Postgres has a real enum type; SQLite
    # stores the column as VARCHAR so no type change is needed there).
    if op.get_bind().dialect.name == "postgresql":
        for value in _NEW_STATUSES:
            op.execute(f"ALTER TYPE appointment_status ADD VALUE IF NOT EXISTS '{value}'")

    # Extend appointments with the cabinet link + consultation record.
    op.add_column(
        "appointments", sa.Column("cabinet_session_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "fk_appointments_cabinet_session_id",
        "appointments",
        "cabinet_sessions",
        ["cabinet_session_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        op.f("ix_appointments_cabinet_session_id"),
        "appointments",
        ["cabinet_session_id"],
        unique=False,
    )
    op.add_column(
        "appointments",
        sa.Column("consultation_started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "appointments",
        sa.Column("consultation_ended_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "appointments", sa.Column("chief_complaint", sa.String(length=1000), nullable=True)
    )
    op.add_column("appointments", sa.Column("symptoms", sa.JSON(), nullable=True))
    op.add_column("appointments", sa.Column("vitals", sa.JSON(), nullable=True))
    op.add_column(
        "appointments", sa.Column("exam_notes", sa.String(length=4000), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("appointments", "exam_notes")
    op.drop_column("appointments", "vitals")
    op.drop_column("appointments", "symptoms")
    op.drop_column("appointments", "chief_complaint")
    op.drop_column("appointments", "consultation_ended_at")
    op.drop_column("appointments", "consultation_started_at")
    op.drop_index(op.f("ix_appointments_cabinet_session_id"), table_name="appointments")
    op.drop_constraint("fk_appointments_cabinet_session_id", "appointments", type_="foreignkey")
    op.drop_column("appointments", "cabinet_session_id")

    op.drop_index(op.f("ix_cabinet_sessions_is_open"), table_name="cabinet_sessions")
    op.drop_index(op.f("ix_cabinet_sessions_opened_at"), table_name="cabinet_sessions")
    op.drop_index(op.f("ix_cabinet_sessions_acting_doctor_id"), table_name="cabinet_sessions")
    op.drop_index(op.f("ix_cabinet_sessions_cabinet_id"), table_name="cabinet_sessions")
    op.drop_table("cabinet_sessions")
    op.drop_index(op.f("ix_cabinets_owner_doctor_id"), table_name="cabinets")
    op.drop_table("cabinets")
    # NOTE: Postgres cannot drop enum values; CHECKED_IN / IN_PROGRESS remain on the
    # appointment_status type after downgrade (harmless — no rows will use them once
    # the flow is rolled back).
