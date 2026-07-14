"""add clinic patients register + appointment link

Revision ID: d4e5f6a7b8c9
Revises: a1b2c3d4e5f6
Create Date: 2026-07-15 00:30:00.000000+00:00
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: str | None = 'a1b2c3d4e5f6'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Doctor-owned patient register. Columns mirror the ClinicPatient model exactly
    # (portable sa.JSON for tags — no server_default, since Postgres `json` has no
    # `=` operator and a lingering default would break alembic's `check`).
    op.create_table(
        "clinic_patients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("doctor_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("full_name", sa.String(length=200), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("sex", sa.String(length=16), nullable=True),
        sa.Column("birth_year", sa.Integer(), nullable=True),
        sa.Column("notes", sa.String(length=2000), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("no_show_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["doctor_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("doctor_id", "user_id", name="uq_clinic_patients_doctor_user"),
    )
    op.create_index(
        op.f("ix_clinic_patients_doctor_id"), "clinic_patients", ["doctor_id"], unique=False
    )
    op.create_index(
        op.f("ix_clinic_patients_user_id"), "clinic_patients", ["user_id"], unique=False
    )
    op.create_index(op.f("ix_clinic_patients_phone"), "clinic_patients", ["phone"], unique=False)

    # Link appointments to the register (nullable; backfilled below).
    op.add_column(
        "appointments",
        sa.Column("clinic_patient_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f("ix_appointments_clinic_patient_id"),
        "appointments",
        ["clinic_patient_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_appointments_clinic_patient_id_clinic_patients",
        "appointments",
        "clinic_patients",
        ["clinic_patient_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Backfill: one register row per distinct (doctor_id, patient_id) already seen in
    # appointments, then point each appointment at its row. Postgres-safe and a no-op
    # on empty tables (the SELECTs yield no rows); idempotent via NOT EXISTS / IS NULL.
    op.execute(
        sa.text(
            """
            INSERT INTO clinic_patients (doctor_id, user_id)
            SELECT DISTINCT a.doctor_id, a.patient_id
            FROM appointments a
            WHERE NOT EXISTS (
                SELECT 1 FROM clinic_patients cp
                WHERE cp.doctor_id = a.doctor_id
                  AND cp.user_id = a.patient_id
            )
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE appointments a
            SET clinic_patient_id = cp.id
            FROM clinic_patients cp
            WHERE cp.doctor_id = a.doctor_id
              AND cp.user_id = a.patient_id
              AND a.clinic_patient_id IS NULL
            """
        )
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_appointments_clinic_patient_id_clinic_patients", "appointments", type_="foreignkey"
    )
    op.drop_index(op.f("ix_appointments_clinic_patient_id"), table_name="appointments")
    op.drop_column("appointments", "clinic_patient_id")

    op.drop_index(op.f("ix_clinic_patients_phone"), table_name="clinic_patients")
    op.drop_index(op.f("ix_clinic_patients_user_id"), table_name="clinic_patients")
    op.drop_index(op.f("ix_clinic_patients_doctor_id"), table_name="clinic_patients")
    op.drop_constraint("uq_clinic_patients_doctor_user", "clinic_patients", type_="unique")
    op.drop_table("clinic_patients")
