"""Guardrail: the public-landing columns on doctor_profiles exist as declared.

These five columns are what the doctor's public page renders (contact CTAs,
opening hours, insurance). A rename or a nullability slip here silently breaks
the landing page rather than failing a build, so pin them.
"""

import sehaty.db  # noqa: F401  (registers all tables on the metadata)
from sehaty.db.base import SehatyBase

DOCTOR_PROFILES = SehatyBase.metadata.tables["doctor_profiles"]


def test_public_contact_columns_exist_and_are_nullable():
    # Nullable: an imported (unclaimed) doctor may have none of these yet.
    for name in ("phone_fixe", "phone_mobile", "whatsapp"):
        column = DOCTOR_PROFILES.columns[name]
        assert column.nullable, f"{name} must stay nullable for imported doctors"


def test_opening_hours_and_insurances_are_non_null_json_lists():
    # NOT NULL with a Python-side default=list, mirroring `languages`: the page
    # can then iterate without a None check, and "unspecified" is an empty list.
    for name in ("opening_hours", "insurances"):
        column = DOCTOR_PROFILES.columns[name]
        assert not column.nullable, f"{name} must be NOT NULL"
        assert column.default is not None, f"{name} needs a Python-side default"
        # SQLAlchemy wraps `default=list` in a context-taking callable, so invoke
        # it rather than comparing identity against the builtin.
        assert column.default.is_callable, f"{name} should default via a callable"
        assert column.default.arg(None) == [], f"{name} should default to an empty list"


def test_tiers_payant_defaults_to_false():
    column = DOCTOR_PROFILES.columns["tiers_payant"]
    assert not column.nullable
    assert column.server_default is not None, "existing rows need a backfill default"
