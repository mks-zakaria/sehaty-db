"""patient ledger: treatment charges + instalment payments

Revision ID: d7e8f9a0b1c2
Revises: c6d7e8f9a0b1
Create Date: 2026-07-21 10:00:00.000000+00:00

A doctor records a treatment charge (e.g. braces) against a register patient
and collects it in partial payments over time; the outstanding balance is
derived, never stored.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d7e8f9a0b1c2"
down_revision: str | None = "c6d7e8f9a0b1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "patient_charges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "doctor_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "clinic_patient_id",
            sa.Integer(),
            sa.ForeignKey("clinic_patients.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("label", sa.String(length=200), nullable=False),
        sa.Column("total_amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("note", sa.String(length=1000), nullable=True),
        sa.Column(
            "created_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_patient_charges_doctor_id", "patient_charges", ["doctor_id"])
    op.create_index(
        "ix_patient_charges_clinic_patient_id", "patient_charges", ["clinic_patient_id"]
    )

    op.create_table(
        "patient_payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "charge_id",
            sa.Integer(),
            sa.ForeignKey("patient_charges.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column(
            "method",
            sa.Enum("CASH", "CARD", "TRANSFER", "CHEQUE", "OTHER", name="patient_payment_method"),
            nullable=False,
        ),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column(
            "created_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_patient_payments_charge_id", "patient_payments", ["charge_id"])


def downgrade() -> None:
    op.drop_index("ix_patient_payments_charge_id", table_name="patient_payments")
    op.drop_table("patient_payments")
    op.drop_index("ix_patient_charges_clinic_patient_id", table_name="patient_charges")
    op.drop_index("ix_patient_charges_doctor_id", table_name="patient_charges")
    op.drop_table("patient_charges")
    sa.Enum(name="patient_payment_method").drop(op.get_bind(), checkfirst=True)
