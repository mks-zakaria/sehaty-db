"""Guardrail: every expected table is registered on SehatyBase.metadata.

If a domain module is not re-exported from sehaty.db.__init__, Alembic
autogenerate would miss (or DROP) its tables. This test fails loudly if so.
"""

import sehaty.db  # noqa: F401  (imports the package, registering all tables)
from sehaty.db.base import SehatyBase

EXPECTED_TABLES = {
    # users + catalogue
    "users",
    "patient_profiles",
    "doctor_profiles",
    "specialties",
    "doctor_specialties",
    # scheduling
    "availabilities",
    "appointments",
    "availability_exceptions",
    # messaging
    "message_threads",
    "messages",
    # patient register
    "clinic_patients",
    # patient treatment ledger (charges + instalment payments)
    "patient_charges",
    "patient_payments",
    # practice staffing
    "doctor_assistants",
    # cabinets (practice room + open shifts)
    "cabinets",
    "cabinet_sessions",
    # pharmacy point-of-sale
    "pharmacy_products",
    "pharmacy_sales",
    "pharmacy_sale_items",
    # clinical
    "medications",
    "prescriptions",
    "prescription_items",
    "pharmacy_stock",
    "dispenses",
    "dispense_items",
    "drug_interactions",
    "notifications",
    "renewal_requests",
    "audit_logs",
    # doctor workspace
    "diagnoses",
    "treatment_feedback",
    "practice_profiles",
    "prescription_templates",
    # appointment confirmations + waitlist
    "waitlist_entries",
    "articles",
    "outbound_messages",
    # public-landing config + analytics
    "doctor_landings",
    "landing_events",
    # reputation
    "reviews",
    "reputation_scores",
    # billing
    "plans",
    "subscriptions",
    "invoices",
    "payments",
    "credit_ledger",
    # referral
    "referrals",
    # admin / config
    "admin_config",
    "feature_flags",
    "ranking_weights",
    # auth support
    "refresh_tokens",
    "phone_otp",
}


def test_expected_tables_registered():
    registered = set(SehatyBase.metadata.tables.keys())
    missing = EXPECTED_TABLES - registered
    assert not missing, f"tables missing from metadata (re-export them): {missing}"


def test_no_unexpected_drops():
    # Every registered table should be one we know about (catches stray/renamed).
    registered = set(SehatyBase.metadata.tables.keys())
    unexpected = registered - EXPECTED_TABLES
    assert not unexpected, f"unexpected tables (update EXPECTED_TABLES): {unexpected}"
