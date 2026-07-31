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

**Two ways an article gets written**, sharing one table because they are the same
object to a reader and to a crawler:

1. *A doctor answers a question.* `author_id` is them; the byline is the
   citation. Everything above describes this shape.
2. *The platform writes from the literature* — anatomy and pathology texts, via
   retrieval — and doctors then validate, rectify or enrich it (see
   `ArticleValidation`). `author_id` is NULL, `sources` carries the works it was
   drawn from, and the standing comes from the doctors who signed it rather than
   from one author.

The second shape exists because waiting for physicians to write does not fill a
directory: it produces a handful of answers in the specialties that already have
enthusiastic doctors, and nothing at all in the rest. Writing first and asking a
doctor to check is a five-minute favour rather than a homework assignment, and it
gives the sales visit a reason to exist that is not a price list.
"""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from sehaty.db.base import SehatyBase, TimestampMixin, utcnow


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
    #
    # NULL for an article the platform wrote from the medical literature. Those
    # carry no personal opinion to orphan — their standing comes from `sources`
    # and from the doctors in `article_validations` who put their name to them.
    author_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    # What a platform-written article was drawn from:
    # ``[{"work": "Gray's Anatomy", "locator": "41e, ch. 12"}]``.
    #
    # Not decoration. An article about a disease that cites nothing is indistinct
    # from an article a machine invented, both to the doctor being asked to put
    # their name to it and to a reader deciding whether to believe it. Empty for
    # doctor-written answers, where the byline is the citation.
    sources: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)

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

    # Illustrations, in two stages:
    #   [{"brief": "what it should show", "alt": "...", "url": ..., "credit": ...}]
    #
    # A draft arrives with briefs and no URLs — the writer can say what a diagram
    # should show, and must not invent the diagram itself. A fabricated medical
    # illustration is worse than none: a reader trusts a picture of an artery far
    # more readily than a sentence about one, and cannot check it.
    #
    # An entry with no `url` renders nothing on the page; it is a note to whoever
    # sources the image.
    images: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)

    status: Mapped[ArticleStatus] = mapped_column(
        Enum(ArticleStatus, name="article_status"), default=ArticleStatus.DRAFT
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Why it was turned down, shown to the author. A rejection nobody can act on
    # is just a wall.
    review_note: Mapped[str | None] = mapped_column(String(500), nullable=True)


class ValidationVerdict(enum.StrEnum):
    """What a doctor did to an article they put their name to.

    Three verdicts rather than a yes/no because they are three different amounts
    of work, and the difference is what a doctor is being credited for. A reader
    weighing an article about their own illness is owed the distinction too:
    "read and agreed with" is not the same claim as "corrected".
    """

    VALIDATED = "VALIDATED"
    # Found something wrong and fixed it — the text changed.
    RECTIFIED = "RECTIFIED"
    # Added to it: a local practice, a caveat, a Moroccan-specific detail.
    ENRICHED = "ENRICHED"


class ArticleValidation(SehatyBase, TimestampMixin):
    """One doctor's endorsement of one article.

    This is the exchange the whole content strategy runs on. The platform writes
    from the literature; a doctor lends their professional standing; in return
    their name appears on a page that ranks, linking back to their own. Neither
    half works alone — an unsigned article is machine text nobody should act on,
    and a doctor with no article has nothing pointing at them.

    One row per doctor per article: a second reading updates their verdict rather
    than stacking endorsements, so five validations means five doctors and not
    one doctor five times.
    """

    __tablename__ = "article_validations"
    __table_args__ = (
        UniqueConstraint("article_id", "doctor_id", name="uq_article_validation_once"),
        # The byline query: every validator of this article.
        Index("ix_article_validations_article", "article_id"),
        # The reverse, for a doctor's page: everything they have put their name to.
        Index("ix_article_validations_doctor", "doctor_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE"), nullable=False
    )
    # Deleting the doctor removes the endorsement: their name must stop appearing
    # on the article the moment their account is gone.
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    verdict: Mapped[ValidationVerdict] = mapped_column(
        Enum(ValidationVerdict, name="validation_verdict"),
        default=ValidationVerdict.VALIDATED,
    )
    # What they changed or added, in their words. Required for RECTIFIED and
    # ENRICHED — a correction nobody can see is indistinguishable from a rubber
    # stamp, and the note is what makes the credit legible.
    note: Mapped[str | None] = mapped_column(Text, nullable=True)


class ArticleVote(SehatyBase, TimestampMixin):
    """One reader saying an article did or did not help them.

    The point is not a score, it is a signal we can act on: an article with a
    hundred readers and a falling helpful rate is one a doctor should be asked to
    correct, which is the loop that makes a directory trustworthy rather than
    merely large.

    `voter_key` is a salted hash — never an IP address, never an account. One
    vote per reader per article, and nothing stored that identifies who they are.
    Health pages are exactly where a browsing record is most sensitive, and a
    vote on an article about depression must not become a record that a
    particular person read about depression.
    """

    __tablename__ = "article_votes"
    __table_args__ = (
        UniqueConstraint("article_id", "voter_key", name="uq_article_vote_once"),
        Index("ix_article_votes_article", "article_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE"), nullable=False
    )
    voter_key: Mapped[str] = mapped_column(String(64), nullable=False)
    helpful: Mapped[bool] = mapped_column(Boolean, nullable=False)


class ArticleEventType(enum.StrEnum):
    """What a reader did with an article."""

    PAGE_VIEW = "PAGE_VIEW"
    # Followed a validating doctor's name to their page. This is the one that
    # matters commercially: it is the proof that signing an article sends a
    # doctor patients, which is the whole consideration we offer them.
    DOCTOR_CLICK = "DOCTOR_CLICK"


class ArticleEvent(SehatyBase):
    """One interaction with a published article.

    Exists because topic selection was running on disease prevalence — a proxy
    for demand, and a poor one. Somebody with cirrhosis may never search for it;
    somebody frightened about their liver searches constantly. Only our own
    traffic can settle which articles are read, and `source` records the channel
    a reader arrived by, so "ranks on Google" and "travels on WhatsApp" stop being
    the same number.

    Same privacy stance as `landing_events`: no IP, no cookie, no identity. A row
    says an article was read, never who read it — which matters more here than on
    a doctor page, because the article title is itself a health disclosure.
    """

    __tablename__ = "article_events"
    __table_args__ = (
        Index("ix_article_events_article_occurred", "article_id", "occurred_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[ArticleEventType] = mapped_column(
        Enum(ArticleEventType, name="article_event_type")
    )
    # Which doctor was followed, on a DOCTOR_CLICK. Null for a page view.
    doctor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
    # Coarse channel only ("google", "whatsapp", "facebook", "direct"). Never a
    # full referrer: a search query typed before landing on an article about
    # depression is health data about the person who typed it.
    source: Mapped[str | None] = mapped_column(String(32), nullable=True)
