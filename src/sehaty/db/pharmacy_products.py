"""Pharmacy point-of-sale: products, sales, and sale lines.

A pharmacy manages its own **products** — over-the-counter items it registers
with a barcode/QR, a name, and a kind (a MEDICINE, optionally linked to the
``medications`` catalogue, or a COSMETIC). Selling scans the barcode, adds lines
to a **sale**, and records the transaction (decrementing product stock). This is
separate from prescription *dispensing* (``dispenses``), which is tied to a
doctor's prescription.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sehaty.db.base import SehatyBase, TimestampMixin


class ProductKind(enum.StrEnum):
    MEDICINE = "MEDICINE"
    COSMETIC = "COSMETIC"


class PharmacyProduct(SehatyBase, TimestampMixin):
    __tablename__ = "pharmacy_products"
    __table_args__ = (
        # One product per (pharmacy, barcode) — the barcode is the scan key.
        UniqueConstraint("pharmacy_id", "barcode", name="uq_pharmacy_products_barcode"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    pharmacy_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    barcode: Mapped[str] = mapped_column(String(128), index=True)
    name: Mapped[str] = mapped_column(String(200))
    kind: Mapped[ProductKind] = mapped_column(Enum(ProductKind, name="product_kind"))
    # Optional link to the medication catalogue when kind is MEDICINE.
    medication_id: Mapped[int | None] = mapped_column(
        ForeignKey("medications.id"), nullable=True
    )
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    low_threshold: Mapped[int] = mapped_column(Integer, default=10)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true"), default=True
    )


class Sale(SehatyBase):
    __tablename__ = "pharmacy_sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    pharmacy_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    sold_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    total: Mapped[float] = mapped_column(Float, default=0.0)

    items: Mapped[list["SaleItem"]] = relationship(
        back_populates="sale", cascade="all, delete-orphan"
    )


class SaleItem(SehatyBase):
    __tablename__ = "pharmacy_sale_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(
        ForeignKey("pharmacy_sales.id", ondelete="CASCADE"), index=True
    )
    # Keep the line if the product is later removed; the snapshot below survives.
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("pharmacy_products.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200))  # snapshot at sale time
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float, default=0.0)
    line_total: Mapped[float] = mapped_column(Float, default=0.0)

    sale: Mapped["Sale"] = relationship(back_populates="items")
