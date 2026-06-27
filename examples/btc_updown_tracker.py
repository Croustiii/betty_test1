"""
Exemple de base : suivi du marché BTC Up/Down 5min synchronisé sur l'horloge système.
Réalise 4 captures par cycle de 5 minutes :
  - OPEN  : début du cycle (dans les 5 premières secondes)
  - MID   : à 2min30 écoulées (t+150s)
  - LATE  : à 3min50 écoulées (t+230s)
  - CLOSE : à la clôture du cycle (t+300s)
"""
import threading
from datetime import datetime

from polymarket import PolymarketClient
from polymarket.config import CacheTTL, IntervalSec
from polymarket.logger import Logger
from polymarket.scheduler import CycleScheduler
from polymarket.utils import MarketUtils


class BtcUpDownTracker:

    def __init__(self, logger: Logger) -> None:
        self._logger = logger
        self._client = PolymarketClient()
        self._current_slug: str = ""
        self._current_thread_id: str = ""
        self._scheduler = CycleScheduler(
            interval_seconds=IntervalSec.VERY_SHORT,
            tick_seconds=30,
            on_cycle_start=self._on_cycle_start,
            on_cycle_end=self._on_cycle_end,
        )

    def _fetch_and_log(self, label: str, slug: str, thread_id: str) -> None:
        call_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self._logger.log(thread_id, label, f"→API {call_time}  get_event_by_slug({slug})")

        event = self._client.get_event_by_slug(slug, ttl=CacheTTL.REALTIME)

        if not event or not event.markets:
            self._logger.log(thread_id, label, f"←    {datetime.now().strftime('%H:%M:%S.%f')[:-3]}  Aucun marché trouvé")
            return

        market = event.markets[0]
        self._client.enrich_with_prices([market])

        resp_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        question_local = MarketUtils.localize_market_question(market.question)
        prices = " | ".join(
            f"{t.outcome}: {t.price:.2%}" for t in market.tokens if t.price is not None
        )
        self._logger.log(thread_id, label, f"←    {resp_time}  {question_local}  →  {prices}")

    def _on_cycle_start(self, cycle_dt: datetime) -> None:
        self._current_thread_id = cycle_dt.strftime("%H:%M")
        self._current_slug = MarketUtils.get_current_btc_updown_5m_slug()
        thread_id = self._current_thread_id
        slug = self._current_slug

        self._fetch_and_log("OPEN ", slug, thread_id)
        threading.Timer(150, self._fetch_and_log, args=("MID  ", slug, thread_id)).start()
        threading.Timer(230, self._fetch_and_log, args=("LATE ", slug, thread_id)).start()

    def _on_cycle_end(self, cycle_dt: datetime) -> None:
        self._fetch_and_log("CLOSE", self._current_slug, self._current_thread_id)

    def run(self) -> None:
        try:
            self._scheduler.run()
        finally:
            self._client.close()


if __name__ == "__main__":
    with Logger() as logger:
        BtcUpDownTracker(logger).run()
