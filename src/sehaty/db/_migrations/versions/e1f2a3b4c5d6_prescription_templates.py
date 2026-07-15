"""prescription templates (reusable doctor presets)

Revision ID: e1f2a3b4c5d6
Revises: d0e1f2a3b4c5
Create Date: 2026-07-15 08:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e1f2a3b4c5d6"
down_revision: str | None = "d0e1f2a3b4c5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # A doctor's reusable, named prescription preset. Columns mirror the
    # PrescriptionTemplate model exactly. The `items` column is portable sa.JSON
    # with NO server_default: Postgres `json` has no `=` operator, so a lingering
    # default would break alembic's autogenerate/`check` comparison. The empty
    # list is supplied Python-side via default=list on the model.
    op.create_table(
        "prescription_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("doctor_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("notes", sa.String(length=2000), nullable=True),
        sa.Column("items", sa.JSON(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["doctor_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_prescription_templates_doctor_id"),
        "prescription_templates",
        ["doctor_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_prescription_templates_doctor_id"), table_name="prescription_templates"
    )
    op.drop_table("prescription_templates")
