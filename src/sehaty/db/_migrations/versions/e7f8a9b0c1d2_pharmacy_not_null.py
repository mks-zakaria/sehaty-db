"""pharmacy columns: enforce the NOT NULL the models already declare

Revision ID: e7f8a9b0c1d2
Revises: d7e8f9a0b1c2
Create Date: 2026-07-27 00:00:00.000000+00:00

The pharmacy models declare these columns non-optional (``Mapped[int]`` /
``Mapped[float]``), but the table that created them left every one nullable.
``alembic check`` has reported the drift on every run since, which is why the
migrate job on main is red.

Each column is backfilled before the constraint goes on, so the migration is
safe against rows that predate it — a bare SET NOT NULL would abort on the
first NULL and leave the deployment half-migrated. Backfill values match the
models' own Python-side defaults, so nothing changes meaning: a stock count
with no value is zero, an unpriced line is zero.
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e7f8a9b0c1d2"
down_revision: str | None = "d7e8f9a0b1c2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# (table, column, type, backfill) — backfill mirrors the model's own default.
_COLUMNS = [
    ("pharmacy_products", "quantity", sa.Integer(), "0"),
    ("pharmacy_products", "low_threshold", sa.Integer(), "10"),
    ("pharmacy_sales", "total", sa.Float(), "0"),
    ("pharmacy_sale_items", "unit_price", sa.Float(), "0"),
    ("pharmacy_sale_items", "line_total", sa.Float(), "0"),
]


def upgrade() -> None:
    for table, column, type_, backfill in _COLUMNS:
        op.execute(
            sa.text(f"UPDATE {table} SET {column} = {backfill} WHERE {column} IS NULL")
        )
        op.alter_column(table, column, existing_type=type_, nullable=False)


def downgrade() -> None:
    for table, column, type_, _backfill in _COLUMNS:
        op.alter_column(table, column, existing_type=type_, nullable=True)
