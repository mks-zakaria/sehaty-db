"""per-language doctor presentation

Revision ID: f1a2b3c4d5e6
Revises: e0f1a2b3c4d5
Create Date: 2026-07-29 06:00:00.000000+00:00

A page renders in French, Arabic and Darija; the presentation behind it was a
single string. Whichever language the doctor dictated at the visit, the other
two showed it verbatim — French prose on an Arabic page.

`bio` stays as the fallback so nothing already published stops rendering.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: str | None = "e0f1a2b3c4d5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # The default exists only to satisfy NOT NULL on rows that already exist;
    # the model does not declare one, so it is dropped again to keep the schema
    # and the model in agreement.
    op.add_column(
        "doctor_profiles",
        sa.Column(
            "bio_i18n", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")
        ),
    )
    op.alter_column("doctor_profiles", "bio_i18n", server_default=None)


def downgrade() -> None:
    op.drop_column("doctor_profiles", "bio_i18n")
