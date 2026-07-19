"""remove stray French-slug specialty rows + backfill darija on the canonical slugs

Revision ID: f3c4d5e6a7b8
Revises: e2b3c4d5f6a7
Create Date: 2026-07-19 14:00:00.000000+00:00

The previous migration seeded provider types under French slugs
(``ophtalmologue``, ``opticien``, …) which duplicate the canonical catalogue
(``ophthalmology``, ``optician``, … — seeded by ``SpecialtyController.seed_defaults``).
This removes those strays and backfills ``name_ary`` (darija) onto the canonical
rows where it is still NULL, so darija works on already-populated databases.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f3c4d5e6a7b8"
down_revision: str | None = "e2b3c4d5f6a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_STRAY_SLUGS = [
    "generaliste", "ophtalmologue", "opticien", "dentiste", "pediatre",
    "dermatologue", "cardiologue", "gynecologue", "orl", "psychiatre",
    "rhumatologue", "gastro", "neurologue", "kinesitherapeute",
]

# (canonical slug, darija) — mirrors _DEFAULT_SPECIALTIES in sehaty-core.
_CANONICAL_ARY = [
    ("generalist", "طبيب ديال العام"),
    ("cardiology", "طبيب ديال القلب"),
    ("gastroenterology", "طبيب ديال المعدة"),
    ("dermatology", "طبيب ديال الجلد"),
    ("pediatrics", "طبيب ديال الدراري"),
    ("dentistry", "طبيب ديال السنان"),
    ("gynecology", "طبيب ديال العيالات"),
    ("ophthalmology", "طبيب ديال العينين"),
    ("optician", "مول النّضاضر"),
    ("otolaryngology", "طبيب ديال الأذن والنيف والحلق"),
    ("psychiatry", "طبيب ديال العقل"),
    ("orthopedics", "طبيب ديال العظام"),
    ("neurology", "طبيب ديال الأعصاب"),
    ("urology", "طبيب ديال المسالك"),
    ("endocrinology", "طبيب ديال الغدد"),
    ("pulmonology", "طبيب ديال الرئة"),
    ("rheumatology", "طبيب ديال المفاصل"),
    ("general_surgery", "جرّاح ديال العام"),
    ("radiology", "طبيب ديال الراديو"),
    ("nephrology", "طبيب ديال الكلاوي"),
]


def upgrade() -> None:
    bind = op.get_bind()
    # Drop the stray French-slug rows (only ones with no linked doctors, to be safe).
    bind.execute(
        sa.text(
            "DELETE FROM specialties WHERE slug IN :slugs "
            "AND id NOT IN (SELECT specialty_id FROM doctor_specialties)"
        ).bindparams(sa.bindparam("slugs", value=_STRAY_SLUGS, expanding=True))
    )
    # Backfill darija on the canonical rows where it is still empty.
    upd = sa.text("UPDATE specialties SET name_ary = :ary WHERE slug = :slug AND name_ary IS NULL")
    for slug, ary in _CANONICAL_ARY:
        bind.execute(upd.bindparams(slug=slug, ary=ary))


def downgrade() -> None:
    # Data-only correction; nothing to roll back structurally.
    pass
