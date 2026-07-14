"""Console script: `sehaty-migrate` → `alembic upgrade head`.

Lets downstream services pip-install sehaty-db and apply migrations
without checking out the repo.
"""

from pathlib import Path

from alembic.config import main as alembic_main


def main() -> None:
    cfg = str(Path(__file__).parent / "alembic.ini")
    alembic_main(argv=["-c", cfg, "upgrade", "head"])


if __name__ == "__main__":
    main()
