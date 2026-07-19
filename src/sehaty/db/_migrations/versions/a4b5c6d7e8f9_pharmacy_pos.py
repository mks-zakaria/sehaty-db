"""pharmacy point-of-sale: products, sales, sale items

Revision ID: a4b5c6d7e8f9
Revises: f3c4d5e6a7b8
Create Date: 2026-07-19 15:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a4b5c6d7e8f9"
down_revision: str | None = "f3c4d5e6a7b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pharmacy_products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pharmacy_id", sa.Integer(), nullable=False),
        sa.Column("barcode", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("kind", sa.Enum("MEDICINE", "COSMETIC", name="product_kind"), nullable=False),
        sa.Column("medication_id", sa.Integer(), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("low_threshold", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["pharmacy_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["medication_id"], ["medications.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pharmacy_id", "barcode", name="uq_pharmacy_products_barcode"),
    )
    op.create_index(
        op.f("ix_pharmacy_products_pharmacy_id"), "pharmacy_products", ["pharmacy_id"], unique=False
    )
    op.create_index(
        op.f("ix_pharmacy_products_barcode"), "pharmacy_products", ["barcode"], unique=False
    )

    op.create_table(
        "pharmacy_sales",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pharmacy_id", sa.Integer(), nullable=False),
        sa.Column(
            "sold_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("total", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["pharmacy_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pharmacy_sales_pharmacy_id"), "pharmacy_sales", ["pharmacy_id"], unique=False
    )
    op.create_index(op.f("ix_pharmacy_sales_sold_at"), "pharmacy_sales", ["sold_at"], unique=False)

    op.create_table(
        "pharmacy_sale_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sale_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Float(), nullable=True),
        sa.Column("line_total", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["sale_id"], ["pharmacy_sales.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["pharmacy_products.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pharmacy_sale_items_sale_id"), "pharmacy_sale_items", ["sale_id"], unique=False
    )


def downgrade() -> None:
    op.drop_table("pharmacy_sale_items")
    op.drop_index(op.f("ix_pharmacy_sales_sold_at"), table_name="pharmacy_sales")
    op.drop_index(op.f("ix_pharmacy_sales_pharmacy_id"), table_name="pharmacy_sales")
    op.drop_table("pharmacy_sales")
    op.drop_index(op.f("ix_pharmacy_products_barcode"), table_name="pharmacy_products")
    op.drop_index(op.f("ix_pharmacy_products_pharmacy_id"), table_name="pharmacy_products")
    op.drop_table("pharmacy_products")
    sa.Enum(name="product_kind").drop(op.get_bind(), checkfirst=True)
