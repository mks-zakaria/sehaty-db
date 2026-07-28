"""Doctor-written answers to the questions patients actually ask.

Two problems, one table.

**Thin pages.** Three thousand directory listings that differ only by name and
street are exactly the shape a search engine crawls and declines to index.
Original medical writing in Arabic is the antidote, and it is the one asset a
competitor cannot scrape back off us.

**Reach beyond driving.** A doctor who wants to publish has to claim their page
first, which turns an imported listing into an onboarded one without anybody
crossing Casablanca. Professional visibility motivates physicians far more
reliably than a subscription discount does.

The unit is a **question**, not an essay. Doctors do not write twelve hundred
words; they will answer "est-ce qu'un diabétique peut jeûner ?" in three
sentences between two patients. That shape also matches how people search, and
it lets several doctors answer the same question — so one good question yields
many pieces of content and a reason for each author to take part.

Nothing reaches the public without review. An answer published under our name
carries our liability, and a doctor whose answer reads as advertising is the one
who answers to the Ordre for it — so the reviewer is checking for promotional
language as much as for clinical sense.
"""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from sehaty.db.base import SehatyBase, TimestampMixin


class ArticleStatus(enum.StrEnum):
    """Where an answer sits between written and public.

    PENDING exists because publication is not the author's decision alone. The
    platform carries the liability for what appears under its name, and a review
    step is the only place to catch advice that is wrong, text that is machine
    generated, or praise that would put the author in front of their council.
    """

    DRAFT = "DRAFT"
    # Submitted by the doctor, waiting for a human to read it.
    PENDING = "PENDING"
    PUBLISHED = "PUBLISHED"
    # Rejected with a reason the author can act on, not a silent disappearance.
    REJECTED = "REJECTED"


class Article(SehatyBase, TimestampMixin):
    """One doctor's answer to one question."""

    __tablename__ = "articles"
    __table_args__ = (
        # A slug is a published URL: unique across the site, forever.
        UniqueConstraint("slug", name="uq_articles_slug"),
        # The public index: everything published, newest first.
        Index("ix_articles_status_published", "status", "published_at"),
        # An author's own list, for their page and their dashboard.
        Index("ix_articles_author", "author_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # The doctor whose name appears on it. Deleting the account removes the
    # answer: it is a professional opinion attributed to a person, and an
    # orphaned one attributed to nobody is worth less than nothing.
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    # "ar", "ary" or "fr". Stored rather than detected: a Darija answer and its
    # Arabic equivalent are different texts, not translations of one another.
    locale: Mapped[str] = mapped_column(String(8), default="ar")

    # The patient's question, as a patient would type it.
    title: Mapped[str] = mapped_column(String(300))
    slug: Mapped[str] = mapped_column(String(320), index=True)
    # One or two sentences used as the meta description and the card summary.
    summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
    body: Mapped[str] = mapped_column(Text)

    # Specialty slug this belongs under, so the answer can surface on the
    # matching city+specialty hub — which is where the search traffic lands.
    specialty_slug: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    status: Mapped[ArticleStatus] = mapped_column(
        Enum(ArticleStatus, name="article_status"), default=ArticleStatus.DRAFT
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Why it was turned down, shown to the author. A rejection nobody can act on
    # is just a wall.
    review_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
