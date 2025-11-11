from contextlib import asynccontextmanager
import sqlite3
from pathlib import Path
from typing import Optional

from fastapi import FastAPI

DB_PATH = Path("/data/urls.db")

DDL = """
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL,
    url_canonical TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_urls_slug ON urls(slug);
"""

def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@asynccontextmanager
async def init_db(app: FastAPI) :
    with get_conn() as c:
        c.executescript(DDL)
    yield

def insert_or_get(conn: sqlite3.Connection, *, url: str, url_canonical: str, slug: str) -> str:
    row = conn.execute("SELECT slug FROM urls WHERE url_canonical = ?", (url_canonical,)).fetchone()
    if row:
        return row["slug"]

    conn.execute(
        "INSERT INTO urls (url, url_canonical, slug) VALUES (?, ?, ?)",
        (url, url_canonical, slug),
    )
    return slug

def get_by_slug(conn: sqlite3.Connection, slug: str) -> Optional[sqlite3.Row]:
    return conn.execute("SELECT * FROM urls WHERE slug = ?", (slug,)).fetchone()

