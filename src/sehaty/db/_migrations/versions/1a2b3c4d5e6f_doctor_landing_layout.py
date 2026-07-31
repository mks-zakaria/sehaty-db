"""a design per doctor, on top of the specialty template

Revision ID: 1a2b3c4d5e6f
Revises: f1a2b3c4d5e6
Create Date: 2026-07-30 00:00:00.000000+00:00

``template`` decides which sections a page has and in what order — that is a
property of the specialty, and it is inherited. It says nothing about what the
page *looks* like, so every doctor was published with the same design.

``layout`` is that second, independent choice: staff pick it per doctor during
the onboarding visit. Nullable, meaning "classic", which is the design every
already-published page has — nobody's printed QR leads somewhere that changed
appearance overnight.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1a2b3c4d5e6f"
down_revision: str | None = "f1a2b3c4d5e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # No server default: NULL is meaningful here ("classic, and nobody chose"),
    # exactly as it is for `template`.
    op.add_column("doctor_landings", sa.Column("layout", sa.String(length=32), nullable=True))


def downgrade() -> None:
    op.drop_column("doctor_landings", "layout")
