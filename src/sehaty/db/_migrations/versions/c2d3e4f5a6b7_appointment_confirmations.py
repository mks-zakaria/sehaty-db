"""appointment confirmation state + outbound message log

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-07-27 00:00:00.000000+00:00
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "c2d3e4f5a6b7"
down_revision: str | None = "b1c2d3e4f5a6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_CONFIRMATION_STATUSES = ("PENDING", "CONFIRMED", "DECLINED", "NO_REPLY")
_CHANNELS = ("WHATSAPP_MANUAL", "WHATSAPP_API", "SMS", "CALL")
_OUTBOUND_STATUSES = ("QUEUED", "SENT", "DELIVERED", "READ", "FAILED")

# Postgres enum types are created explicitly below, so every column reference
# must use `create_type=False`. A plain `sa.Enum` re-emits CREATE TYPE when it is
# attached to a column, which collides with the explicit create and aborts the
# migration with "type ... already exists".



def upgrade() -> None:
    bind = op.get_bind()
    sa.Enum(*_CONFIRMATION_STATUSES, name="confirmation_status").create(bind, checkfirst=True)
    sa.Enum(*_CHANNELS, name="confirmation_channel").create(bind, checkfirst=True)
    sa.Enum(*_OUTBOUND_STATUSES, name="outbound_status").create(bind, checkfirst=True)

    confirmation_status = postgresql.ENUM(
        *_CONFIRMATION_STATUSES, name="confirmation_status", create_type=False
    )
    channel = postgresql.ENUM(*_CHANNELS, name="confirmation_channel", create_type=False)
    outbound_status = postgresql.ENUM(
        *_OUTBOUND_STATUSES, name="outbound_status", create_type=False
    )

    op.add_column(
        "appointments",
        sa.Column(
            "confirmation_status",
            confirmation_status,
            nullable=False,
            server_default=sa.text("'PENDING'"),
        ),
    )
    op.add_column(
        "appointments",
        sa.Column("confirmation_sent_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "appointments",
        sa.Column("confirmation_replied_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "appointments", sa.Column("confirmation_channel", channel, nullable=True)
    )
    op.add_column(
        "appointments",
        sa.Column("no_show_score", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )
    # The secretary's day view filters on it; the T-24h job scans for PENDING.
    op.create_index(
        "ix_appointments_confirmation_status", "appointments", ["confirmation_status"]
    )

    op.create_table(
        "outbound_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "appointment_id",
            sa.Integer(),
            sa.ForeignKey("appointments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("channel", channel, nullable=False),
        sa.Column("template", sa.String(64), nullable=True),
        sa.Column("status", outbound_status, nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("provider_message_id", sa.String(128), nullable=True),
        # Thousandths of a centime — integer arithmetic, no float drift.
        sa.Column("cost_micros", sa.Integer(), nullable=True),
        sa.Column("error", sa.String(400), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_outbound_messages_appointment_id", "outbound_messages", ["appointment_id"]
    )
    op.create_index("ix_outbound_messages_sent_at", "outbound_messages", ["sent_at"])
    op.create_index(
        "ix_outbound_messages_appt_sent", "outbound_messages", ["appointment_id", "sent_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_outbound_messages_appt_sent", table_name="outbound_messages")
    op.drop_index("ix_outbound_messages_sent_at", table_name="outbound_messages")
    op.drop_index("ix_outbound_messages_appointment_id", table_name="outbound_messages")
    op.drop_table("outbound_messages")

    op.drop_index("ix_appointments_confirmation_status", table_name="appointments")
    op.drop_column("appointments", "no_show_score")
    op.drop_column("appointments", "confirmation_channel")
    op.drop_column("appointments", "confirmation_replied_at")
    op.drop_column("appointments", "confirmation_sent_at")
    op.drop_column("appointments", "confirmation_status")

    bind = op.get_bind()
    sa.Enum(name="outbound_status").drop(bind, checkfirst=True)
    sa.Enum(name="confirmation_channel").drop(bind, checkfirst=True)
    sa.Enum(name="confirmation_status").drop(bind, checkfirst=True)
