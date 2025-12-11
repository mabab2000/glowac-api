"""Database utilities for the Glowac API."""

import os
from pathlib import Path
from typing import Dict, Optional

try:
    import psycopg
    from psycopg import sql
    from psycopg.conninfo import conninfo_to_dict, make_conninfo
except ImportError as exc:  # pragma: no cover - dependency guidance
    raise SystemExit(
        "Required dependencies missing. Install with 'pip install -r requirements.txt' before rerunning."
    ) from exc

_DATABASE_URL: Optional[str] = None
_CONNINFO: Optional[Dict[str, str]] = None
_DSN: Optional[str] = None


def _read_database_url_from_env_file() -> Optional[str]:
    env_path = Path(".env")
    if not env_path.is_file():
        return None
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if key.strip() == "DATABASE_URL" and sep:
            return value.strip().strip('"').strip("'")
    return None


def get_database_url() -> str:
    """Return the DATABASE_URL from environment or .env file."""

    global _DATABASE_URL
    if _DATABASE_URL is None:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            db_url = _read_database_url_from_env_file()
        if not db_url:
            raise SystemExit("DATABASE_URL is not set; define it in the environment or .env file.")
        _DATABASE_URL = db_url
    return _DATABASE_URL


def get_conninfo() -> Dict[str, str]:
    """Parse DATABASE_URL into psycopg connection options."""

    global _CONNINFO
    if _CONNINFO is None:
        conninfo = conninfo_to_dict(get_database_url())
        dbname = conninfo.get("dbname")
        if not dbname:
            raise SystemExit("DATABASE_URL must include a database name (dbname component).")
        _CONNINFO = conninfo
    return dict(_CONNINFO)


def get_dsn() -> str:
    """Return a DSN string for connecting to the target database."""

    global _DSN
    if _DSN is None:
        _DSN = make_conninfo(**get_conninfo())
    return _DSN


def ensure_database() -> None:
    """Create the target database when it does not exist yet."""

    conninfo = get_conninfo()
    admin_conninfo = {**conninfo, "dbname": "postgres"}
    admin_dsn = make_conninfo(**admin_conninfo)
    target_db = conninfo["dbname"]

    with psycopg.connect(admin_dsn, autocommit=True) as admin_conn:
        with admin_conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
            if cur.fetchone():
                return
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_db)))


def ensure_banner_table() -> None:
    """Create the banner table if missing inside the target database."""

    dsn = get_dsn()
    with psycopg.connect(dsn, autocommit=True) as db_conn:
        with db_conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS banner (
                    id BIGSERIAL PRIMARY KEY,
                    highlight_tag TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    image BYTEA,
                    image_mime TEXT
                )
                """
            )
            cur.execute(
                """
                ALTER TABLE banner
                ADD COLUMN IF NOT EXISTS image_mime TEXT
                """
            )


__all__ = [
    "ensure_database",
    "ensure_banner_table",
    "get_conninfo",
    "get_dsn",
]

def ensure_tus_table() -> None:
    """Create the tus table (opening hours entries) if missing."""

    dsn = get_dsn()
    with psycopg.connect(dsn, autocommit=True) as db_conn:
        with db_conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tus (
                    id BIGSERIAL PRIMARY KEY,
                    day TEXT NOT NULL,
                    hours TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Open'
                )
                """
            )

__all__.append("ensure_tus_table")


def ensure_facts_table() -> None:
    """Create the facts table (homepage stats) if missing."""

    dsn = get_dsn()
    with psycopg.connect(dsn, autocommit=True) as db_conn:
        with db_conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS facts (
                    id BIGSERIAL PRIMARY KEY,
                    label TEXT NOT NULL,
                    number BIGINT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Visible'
                )
                """
            )

__all__.append("ensure_facts_table")


def ensure_why_table() -> None:
    """Create the why_choose_us table if missing."""

    dsn = get_dsn()
    with psycopg.connect(dsn, autocommit=True) as db_conn:
        with db_conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS why_choose_us (
                    id BIGSERIAL PRIMARY KEY,
                    label TEXT NOT NULL,
                    value TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Visible'
                )
                """
            )

__all__.append("ensure_why_table")


def ensure_background_table() -> None:
    """Create the background table (paragraph entries) if missing."""

    dsn = get_dsn()
    with psycopg.connect(dsn, autocommit=True) as db_conn:
        with db_conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS background (
                    id BIGSERIAL PRIMARY KEY,
                    paragraph TEXT NOT NULL
                )
                """
            )

__all__.append("ensure_background_table")


def ensure_core_values_table() -> None:
    """Create the core_values table (bullet points) if missing."""

    dsn = get_dsn()
    with psycopg.connect(dsn, autocommit=True) as db_conn:
        with db_conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS core_values (
                    id BIGSERIAL PRIMARY KEY,
                    bullet_text TEXT NOT NULL
                )
                """
            )

__all__.append("ensure_core_values_table")


def ensure_gallery_table() -> None:
    """Create the gallery table (image uploads) if missing."""

    dsn = get_dsn()
    with psycopg.connect(dsn, autocommit=True) as db_conn:
        with db_conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS gallery (
                    id BIGSERIAL PRIMARY KEY,
                    image BYTEA NOT NULL,
                    image_mime TEXT
                )
                """
            )

__all__.append("ensure_gallery_table")


def ensure_ceo_table() -> None:
    """Create the ceo_card table for CEO Card entries if missing."""

    dsn = get_dsn()
    with psycopg.connect(dsn, autocommit=True) as db_conn:
        with db_conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS ceo_card (
                    id BIGSERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    email TEXT NOT NULL,
                    image_url TEXT,
                    short_description TEXT
                )
                """
            )
            # ensure columns for storing uploaded image bytes and mime are present
            cur.execute(
                """
                ALTER TABLE ceo_card
                ADD COLUMN IF NOT EXISTS image BYTEA,
                ADD COLUMN IF NOT EXISTS image_mime TEXT
                """
            )

__all__.append("ensure_ceo_table")


def ensure_members_table() -> None:
    """Create the members table (team members) if missing."""

    dsn = get_dsn()
    with psycopg.connect(dsn, autocommit=True) as db_conn:
        with db_conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS members (
                    id BIGSERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    email TEXT NOT NULL,
                    image_url TEXT,
                    short_description TEXT
                )
                """
            )
            # ensure columns for storing uploaded image bytes and mime are present
            cur.execute(
                """
                ALTER TABLE members
                ADD COLUMN IF NOT EXISTS image BYTEA,
                ADD COLUMN IF NOT EXISTS image_mime TEXT
                """
            )

__all__.append("ensure_members_table")


def ensure_main_service_table() -> None:
    """Create the main_service table if missing."""

    dsn = get_dsn()
    with psycopg.connect(dsn, autocommit=True) as db_conn:
        with db_conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS main_service (
                    id BIGSERIAL PRIMARY KEY,
                    service_name TEXT NOT NULL
                )
                """
            )

__all__.append("ensure_main_service_table")


def ensure_sub_service_table() -> None:
    """Create the sub_service table if missing.

    Each sub_service references a main_service via main_service_id.
    """

    dsn = get_dsn()
    with psycopg.connect(dsn, autocommit=True) as db_conn:
        with db_conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS sub_service (
                    id BIGSERIAL PRIMARY KEY,
                    main_service_id BIGINT NOT NULL REFERENCES main_service(id) ON DELETE CASCADE,
                    service_name TEXT NOT NULL,
                    description TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sub_service_main_id ON sub_service(main_service_id)
                """
            )

__all__.append("ensure_sub_service_table")


def ensure_service_test_table() -> None:
    """Create the service_test table if missing.

    Fields: id, main_service_id (FK), sub_service_id (FK), test_name, description
    """

    dsn = get_dsn()
    with psycopg.connect(dsn, autocommit=True) as db_conn:
        with db_conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS service_test (
                    id BIGSERIAL PRIMARY KEY,
                    main_service_id BIGINT NOT NULL REFERENCES main_service(id) ON DELETE CASCADE,
                    sub_service_id BIGINT NOT NULL REFERENCES sub_service(id) ON DELETE CASCADE,
                    test_name TEXT NOT NULL,
                    description TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_service_test_sub_id ON service_test(sub_service_id)
                """
            )

__all__.append("ensure_service_test_table")
