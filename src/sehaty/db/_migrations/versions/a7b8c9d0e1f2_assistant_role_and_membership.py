"""add ASSISTANT role and doctor-assistant membership

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-07-15 04:00:00.000000+00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a7b8c9d0e1f2"
down_revision: str | None = "f6a7b8c9d0e1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1) Add the new ASSISTANT value to the Postgres `user_role` enum.
    #
    # Postgres forbids `ALTER TYPE ... ADD VALUE` inside a transaction block that then
    # USES the new value, so it must be committed on its own. Alembic wraps every
    # migration in a transaction, so we escape it via autocommit_block(). IF NOT EXISTS
    # keeps it idempotent across the CI up -> down -> up cycle (downgrade does NOT
    # remove the value — see below). The DO block guards the SQLite/typeless path:
    # if the `user_role` type does not exist (e.g. non-Postgres), it is a no-op.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        with op.get_context().autocommit_block():
            op.execute(
                sa.text(
                    """
                    DO $$
                    BEGIN
                        IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
                            ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'ASSISTANT';
                        END IF;
                    END
                    $$;
                    """
                )
            )

    # 2) doctor_assistants: links an ASSISTANT user to the doctor(s) they work for.
    op.create_table(
        "doctor_assistants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("doctor_id", sa.Integer(), nullable=False),
        sa.Column("assistant_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["doctor_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["assistant_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("doctor_id", "assistant_id", name="uq_doctor_assistants_pair"),
    )
    op.create_index(
        op.f("ix_doctor_assistants_doctor_id"), "doctor_assistants", ["doctor_id"], unique=False
    )
    op.create_index(
        op.f("ix_doctor_assistants_assistant_id"),
        "doctor_assistants",
        ["assistant_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_doctor_assistants_assistant_id"), table_name="doctor_assistants")
    op.drop_index(op.f("ix_doctor_assistants_doctor_id"), table_name="doctor_assistants")
    op.drop_constraint("uq_doctor_assistants_pair", "doctor_assistants", type_="unique")
    op.drop_table("doctor_assistants")

    # NOTE: the 'ASSISTANT' value added to the `user_role` enum is intentionally NOT
    # removed here. Postgres does not support removing a value from an enum type
    # (there is no `ALTER TYPE ... DROP VALUE`), so this is a documented, irreversible
    # part of the upgrade. Leaving the value in place is harmless and keeps the
    # up -> down -> up cycle idempotent (ADD VALUE IF NOT EXISTS is a no-op on re-up).
