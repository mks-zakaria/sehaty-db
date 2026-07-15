"""add doctor workspace: diagnoses, treatment feedback, practice profiles, freehand prescriptions

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-07-15 03:00:00.000000+00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e5f6a7b8c9d0"
down_revision: str | None = "d4e5f6a7b8c9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- practice_profiles (doctor letterheads) ---------------------------------
    op.create_table(
        "practice_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("doctor_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("clinic_name", sa.String(length=200), nullable=True),
        sa.Column("address", sa.String(length=300), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("header_line", sa.String(length=300), nullable=True),
        sa.Column("signature_name", sa.String(length=160), nullable=True),
        sa.Column("signature_image_url", sa.String(length=500), nullable=True),
        sa.Column("watermark_text", sa.String(length=120), nullable=True),
        sa.Column("watermark_image_url", sa.String(length=500), nullable=True),
        sa.Column("is_default", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["doctor_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_practice_profiles_doctor_id"), "practice_profiles", ["doctor_id"], unique=False
    )

    # --- diagnoses --------------------------------------------------------------
    op.create_table(
        "diagnoses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("doctor_id", sa.Integer(), nullable=False),
        sa.Column("clinic_patient_id", sa.Integer(), nullable=True),
        sa.Column("appointment_id", sa.Integer(), nullable=True),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("icd10", sa.String(length=16), nullable=True),
        sa.Column("notes", sa.String(length=2000), nullable=True),
        sa.Column("diagnosed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["doctor_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["clinic_patient_id"], ["clinic_patients.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointments.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_diagnoses_doctor_id"), "diagnoses", ["doctor_id"], unique=False)
    op.create_index(
        op.f("ix_diagnoses_clinic_patient_id"), "diagnoses", ["clinic_patient_id"], unique=False
    )

    # --- treatment_feedback -----------------------------------------------------
    # sa.Enum inside create_table creates the `treatment_outcome` type on Postgres
    # and is a no-op VARCHAR check on SQLite (portable across both backends).
    op.create_table(
        "treatment_feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("clinic_patient_id", sa.Integer(), nullable=False),
        sa.Column("author_user_id", sa.Integer(), nullable=True),
        sa.Column("target_type", sa.String(length=24), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column(
            "outcome",
            sa.Enum("BETTER", "SAME", "WORSE", name="treatment_outcome"),
            nullable=False,
        ),
        sa.Column("comment", sa.String(length=1000), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["clinic_patient_id"], ["clinic_patients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["author_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_treatment_feedback_clinic_patient_id"),
        "treatment_feedback",
        ["clinic_patient_id"],
        unique=False,
    )

    # --- freehand prescriptions -------------------------------------------------
    # Catalog link becomes optional; free-text drug/instructions carry the rest.
    op.alter_column(
        "prescription_items", "medication_id", existing_type=sa.Integer(), nullable=True
    )
    op.add_column(
        "prescription_items", sa.Column("drug_name", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "prescription_items", sa.Column("instructions", sa.String(length=500), nullable=True)
    )

    # Prescriptions gain a letterhead reference + free-text body.
    op.add_column("prescriptions", sa.Column("practice_profile_id", sa.Integer(), nullable=True))
    op.add_column("prescriptions", sa.Column("notes", sa.String(length=2000), nullable=True))
    op.create_foreign_key(
        "fk_prescriptions_practice_profile_id_practice_profiles",
        "prescriptions",
        "practice_profiles",
        ["practice_profile_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_prescriptions_practice_profile_id_practice_profiles",
        "prescriptions",
        type_="foreignkey",
    )
    op.drop_column("prescriptions", "notes")
    op.drop_column("prescriptions", "practice_profile_id")

    op.drop_column("prescription_items", "instructions")
    op.drop_column("prescription_items", "drug_name")
    op.alter_column(
        "prescription_items", "medication_id", existing_type=sa.Integer(), nullable=False
    )

    op.drop_index(op.f("ix_treatment_feedback_clinic_patient_id"), table_name="treatment_feedback")
    op.drop_table("treatment_feedback")

    op.drop_index(op.f("ix_diagnoses_clinic_patient_id"), table_name="diagnoses")
    op.drop_index(op.f("ix_diagnoses_doctor_id"), table_name="diagnoses")
    op.drop_table("diagnoses")

    op.drop_index(op.f("ix_practice_profiles_doctor_id"), table_name="practice_profiles")
    op.drop_table("practice_profiles")

    # Alembic's drop_table leaves the Postgres ENUM behind; drop it explicitly so a
    # re-upgrade doesn't hit "type already exists". No-op / IF EXISTS on SQLite path.
    op.execute("DROP TYPE IF EXISTS treatment_outcome")
