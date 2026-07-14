import os
from collections.abc import MutableMapping
from logging.config import fileConfig
from typing import Literal

from alembic import context
from dotenv import find_dotenv, load_dotenv
from geoalchemy2 import alembic_helpers
from sqlalchemy import create_engine, pool

from sehaty.db import *  # noqa: F401, F403  — register every table on metadata
from sehaty.db.base import SehatyBase

load_dotenv(find_dotenv(usecwd=True))

DB_URL = os.environ.get("DATABASE_URL") or os.environ.get("DB_URL")
if not DB_URL:
    raise RuntimeError(
        "Set DATABASE_URL (or DB_URL) before running alembic. Source .env or env-example first."
    )

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SehatyBase.metadata

ObjectType = Literal[
    "schema", "table", "column", "index", "unique_constraint", "foreign_key_constraint"
]


def include_name(
    name: str | None,
    type_: ObjectType,
    parent_names: MutableMapping[str, str | None],
) -> bool:
    # Only manage tables we define in our metadata — never touch PostGIS-managed
    # tables (spatial_ref_sys, the tiger geocoder, topology, etc.).
    if type_ == "table":
        return name is None or name in target_metadata.tables
    if type_ in ("index", "column", "unique_constraint", "foreign_key_constraint"):
        parent = parent_names.get("table_name")
        return parent is None or parent in target_metadata.tables
    return True


# GeoAlchemy2 helpers: exclude auto-managed spatial indexes from autogenerate,
# render Geography types (with their import), and order spatial ops correctly.
def include_object(obj, name, type_, reflected, compare_to):
    return alembic_helpers.include_object(obj, name, type_, reflected, compare_to)


_COMMON = dict(
    target_metadata=target_metadata,
    include_name=include_name,
    include_object=include_object,
    render_item=alembic_helpers.render_item,
    process_revision_directives=alembic_helpers.writer,
    compare_type=True,
    compare_server_default=True,
)


def run_migrations_offline() -> None:
    context.configure(
        url=DB_URL,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **_COMMON,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(DB_URL, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, **_COMMON)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
