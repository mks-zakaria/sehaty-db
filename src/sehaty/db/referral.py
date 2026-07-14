"""Referral models: doctors refer doctors; rewards post to the credit ledger."""

import enum

from sqlalchemy import Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from sehaty.db.base import SehatyBase, TimestampMixin


class ReferralStatus(enum.StrEnum):
    PENDING = "PENDING"
    REWARDED = "REWARDED"
    EXPIRED = "EXPIRED"


class Referral(SehatyBase, TimestampMixin):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(primary_key=True)
    referrer_doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    referred_doctor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    code: Mapped[str] = mapped_column(String(32), index=True)
    status: Mapped[ReferralStatus] = mapped_column(
        Enum(ReferralStatus, name="referral_status"),
        default=ReferralStatus.PENDING,
    )
    reward_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    credit_ledger_id: Mapped[int | None] = mapped_column(
        ForeignKey("credit_ledger.id"), nullable=True
    )
