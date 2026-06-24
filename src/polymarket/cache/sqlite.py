import hashlib
import json
import sqlite3
import time

from polymarket.config import CACHE_DB_PATH


class SqliteCache:
    def __init__(self, db_path: str = CACHE_DB_PATH):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._setup()

    def _setup(self) -> None:
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                expires_at REAL NOT NULL
            )
        """)
        self._conn.commit()

    def _make_key(self, url: str, params: dict | None) -> str:
        raw = f"{url}?{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, url: str, params: dict | None = None) -> dict | list | None:
        key = self._make_key(url, params)
        row = self._conn.execute(
            "SELECT value, expires_at FROM cache WHERE key = ?", (key,)
        ).fetchone()
        if row is None:
            return None
        value, expires_at = row
        if time.time() > expires_at:
            self._conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            self._conn.commit()
            return None
        return json.loads(value)

    def set(self, url: str, params: dict | None, data: dict | list, ttl: int) -> None:
        if ttl == 0:
            return
        key = self._make_key(url, params)
        self._conn.execute(
            "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
            (key, json.dumps(data), time.time() + ttl),
        )
        self._conn.commit()

    def clear_expired(self) -> None:
        self._conn.execute("DELETE FROM cache WHERE expires_at < ?", (time.time(),))
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "SqliteCache":
        return self

    def __exit__(self, *args) -> None:
        self.close()
