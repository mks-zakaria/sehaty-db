"""link prescriptions to clinic patients (support walk-ins)

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-07-15 03:30:00.000000+00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f6a7b8c9d0e1"
down_revision: str | None = "e5f6a7b8c9d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # A prescription now targets a register patient (clinic_patient_id), so it can be
    # issued for ANY patient in a doctor's register, including walk-ins with no app
    # account. patient_id stays as the app-user link when the target has an account.
    op.add_column(
        "prescriptions", sa.Column("clinic_patient_id", sa.Integer(), nullable=True)
    )
    op.create_index(
        op.f("ix_prescriptions_clinic_patient_id"),
        "prescriptions",
        ["clinic_patient_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_prescriptions_clinic_patient_id_clinic_patients",
        "prescriptions",
        "clinic_patients",
        ["clinic_patient_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # patient_id becomes nullable: walk-in prescriptions have no app user.
    op.alter_column(
        "prescriptions", "patient_id", existing_type=sa.Integer(), nullable=True
    )

    # Backfill: point existing prescriptions at the matching register row on
    # (doctor_id, user_id=patient_id). Postgres-safe UPDATE..FROM and a no-op on
    # empty tables; idempotent via the IS NULL guard.
    op.execute(
        sa.text(
            """
            UPDATE prescriptions p
            SET clinic_patient_id = cp.id
            FROM clinic_patients cp
            WHERE cp.doctor_id = p.doctor_id
              AND cp.user_id = p.patient_id
              AND p.clinic_patient_id IS NULL
            """
        )
    )


def downgrade() -> None:
    # Restoring NOT NULL is only safe if no walk-in (NULL patient_id) rows exist,
    # which is acceptable for a downgrade.
    op.alter_column(
        "prescriptions", "patient_id", existing_type=sa.Integer(), nullable=False
    )
    op.drop_constraint(
        "fk_prescriptions_clinic_patient_id_clinic_patients",
        "prescriptions",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_prescriptions_clinic_patient_id"), table_name="prescriptions"
    )
    op.drop_column("prescriptions", "clinic_patient_id")
