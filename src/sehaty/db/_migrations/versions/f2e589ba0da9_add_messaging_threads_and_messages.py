"""add messaging threads and messages

Revision ID: f2e589ba0da9
Revises: e1f2a3b4c5d6
Create Date: 2026-07-16 00:45:52.886996+00:00
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2e589ba0da9'
down_revision: str | None = 'e1f2a3b4c5d6'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1:1 patient<->clinic conversation. Columns mirror the MessageThread model
    # exactly; last_message_at is indexed for inbox sorting and the (patient_id,
    # doctor_id) unique constraint enforces one thread per pair.
    op.create_table('message_threads',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('patient_last_read_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('doctor_last_read_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('patient_id', 'doctor_id', name='uq_message_threads_patient_doctor')
    )
    op.create_index(op.f('ix_message_threads_doctor_id'), 'message_threads', ['doctor_id'], unique=False)
    op.create_index(op.f('ix_message_threads_last_message_at'), 'message_threads', ['last_message_at'], unique=False)
    op.create_index(op.f('ix_message_threads_patient_id'), 'message_threads', ['patient_id'], unique=False)
    # Messages belonging to a thread. sender_id is the actual author (patient,
    # doctor, or the doctor's assistant); created_at is indexed for ordering.
    op.create_table('messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('thread_id', sa.Integer(), nullable=False),
    sa.Column('sender_id', sa.Integer(), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['thread_id'], ['message_threads.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_created_at'), 'messages', ['created_at'], unique=False)
    op.create_index(op.f('ix_messages_sender_id'), 'messages', ['sender_id'], unique=False)
    op.create_index(op.f('ix_messages_thread_id'), 'messages', ['thread_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_messages_thread_id'), table_name='messages')
    op.drop_index(op.f('ix_messages_sender_id'), table_name='messages')
    op.drop_index(op.f('ix_messages_created_at'), table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_message_threads_patient_id'), table_name='message_threads')
    op.drop_index(op.f('ix_message_threads_last_message_at'), table_name='message_threads')
    op.drop_index(op.f('ix_message_threads_doctor_id'), table_name='message_threads')
    op.drop_table('message_threads')
