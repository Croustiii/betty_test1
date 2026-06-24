import json
import sqlite3
import time

from polymarket.config import CACHE_DB_PATH
from polymarket.models.market import Event


class EventStore:
    """Persiste les événements Polymarket dans une table SQLite dédiée."""

    def __init__(self, db_path: str = CACHE_DB_PATH):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._setup()

    def _setup(self) -> None:
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id          TEXT PRIMARY KEY,
                slug        TEXT,
                title       TEXT NOT NULL,
                ticker      TEXT,
                active      INTEGER NOT NULL,
                closed      INTEGER NOT NULL,
                start_date  TEXT,
                end_date    TEXT,
                liquidity   REAL,
                volume      REAL,
                volume_24hr REAL,
                market_count INTEGER,
                markets_json TEXT,
                fetched_at  REAL NOT NULL
            )
        """)
        self._conn.commit()

    def upsert(self, events: list[Event]) -> int:
        """Insère ou met à jour les événements. Retourne le nombre de lignes affectées."""
        now = time.time()
        rows = [
            (
                e.id,
                e.slug,
                e.title,
                e.ticker,
                int(e.active),
                int(e.closed),
                e.start_date.isoformat() if e.start_date else None,
                e.end_date.isoformat() if e.end_date else None,
                e.liquidity,
                e.volume,
                e.volume_24hr,
                len(e.markets),
                json.dumps([
                    {
                        "condition_id": m.condition_id,
                        "question": m.question,
                        "slug": m.slug,
                        "active": m.active,
                        "liquidity": m.liquidity,
                        "volume_24hr": m.volume_24hr,
                        "outcomes": m.outcomes,
                        "outcome_prices": m.outcome_prices,
                    }
                    for m in e.markets
                ]),
                now,
            )
            for e in events
        ]
        self._conn.executemany(
            """
            INSERT OR REPLACE INTO events
                (id, slug, title, ticker, active, closed, start_date, end_date,
                 liquidity, volume, volume_24hr, market_count, markets_json, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        self._conn.commit()
        return len(rows)

    def count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "EventStore":
        return self

    def __exit__(self, *args) -> None:
        self.close()
