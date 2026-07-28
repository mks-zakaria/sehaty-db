"""stop badging doctors nobody has spoken to

Revision ID: e0f1a2b3c4d5
Revises: d9e0f1a2b3c4
Create Date: 2026-07-28 23:12:00.000000+00:00

The importer marked every page VERIFIED because the public read refused to
render anything else — so publishing the directory required claiming we had
checked ~3,650 licences we had never seen. This moves the never-contacted ones
to LISTED, which renders identically minus the badge.

Scoped deliberately: only rows that came from an import *and* were never
claimed. A doctor an operator accredited in person keeps VERIFIED, because
there a human did decide.
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e0f1a2b3c4d5"
down_revision: str | None = "d9e0f1a2b3c4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE doctor_profiles
           SET verification_status = 'LISTED'
         WHERE verification_status = 'VERIFIED'
           AND source = 'IMPORT'
           AND claim_status = 'UNCLAIMED'
        """
    )


def downgrade() -> None:
    op.execute(
        "UPDATE doctor_profiles SET verification_status = 'VERIFIED' "
        "WHERE verification_status = 'LISTED'"
    )
