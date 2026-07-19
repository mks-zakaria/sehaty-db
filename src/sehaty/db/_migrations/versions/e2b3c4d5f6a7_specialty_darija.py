"""add name_ary (darija) to specialties + seed common provider types

Revision ID: e2b3c4d5f6a7
Revises: d1a2c3b4e5f6
Create Date: 2026-07-19 13:00:00.000000+00:00

Adds a Moroccan-Arabic (darija) label to the specialties catalogue (which doubles
as the doctor "type" taxonomy) and seeds a starter set of common provider types
with fr / ar / darija names. The seed is idempotent: it inserts missing types and
backfills ``name_ary`` on existing ones. Darija strings are a reasonable starting
point and are meant to be curated.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e2b3c4d5f6a7"
down_revision: str | None = "d1a2c3b4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# (slug, name_en, name_fr, name_ar, name_ary)
_TYPES = [
    ("generaliste", "General practitioner", "Médecin généraliste", "طبيب عام", "طبيب ديال العام"),
    ("ophtalmologue", "Ophthalmologist", "Ophtalmologue", "طبيب العيون", "طبيب ديال العينين"),
    ("opticien", "Optician", "Opticien", "أخصائي البصريات", "مول النّضاضر"),
    ("dentiste", "Dentist", "Dentiste", "طبيب الأسنان", "طبيب ديال السنان"),
    ("pediatre", "Pediatrician", "Pédiatre", "طبيب الأطفال", "طبيب ديال الدراري"),
    ("dermatologue", "Dermatologist", "Dermatologue", "طبيب الأمراض الجلدية", "طبيب ديال الجلد"),
    ("cardiologue", "Cardiologist", "Cardiologue", "طبيب القلب", "طبيب ديال القلب"),
    ("gynecologue", "Gynecologist", "Gynécologue", "طبيب النساء والتوليد", "طبيب ديال العيالات"),
    ("orl", "ENT specialist", "Oto-rhino-laryngologiste", "طبيب الأنف والأذن والحنجرة",
     "طبيب ديال الأذن والنيف والحلق"),
    ("psychiatre", "Psychiatrist", "Psychiatre", "طبيب نفسي", "طبيب ديال العقل"),
    ("rhumatologue", "Rheumatologist", "Rhumatologue", "طبيب الروماتيزم", "طبيب ديال المفاصل"),
    ("gastro", "Gastroenterologist", "Gastro-entérologue", "طبيب الجهاز الهضمي", "طبيب ديال المعدة"),
    ("neurologue", "Neurologist", "Neurologue", "طبيب الأعصاب", "طبيب ديال الأعصاب"),
    ("kinesitherapeute", "Physiotherapist", "Kinésithérapeute", "أخصائي العلاج الطبيعي",
     "مول الكيني"),
]


def upgrade() -> None:
    op.add_column("specialties", sa.Column("name_ary", sa.String(length=128), nullable=True))
    # Seed / backfill only on Postgres (uses ON CONFLICT). SQLite is test-only and
    # builds its schema from the models, not this migration.
    if op.get_bind().dialect.name == "postgresql":
        stmt = sa.text(
            "INSERT INTO specialties (slug, name_en, name_fr, name_ar, name_ary) "
            "VALUES (:slug, :en, :fr, :ar, :ary) "
            "ON CONFLICT (slug) DO UPDATE SET name_ary = EXCLUDED.name_ary"
        )
        for slug, en, fr, ar, ary in _TYPES:
            op.execute(stmt.bindparams(slug=slug, en=en, fr=fr, ar=ar, ary=ary))


def downgrade() -> None:
    op.drop_column("specialties", "name_ary")
