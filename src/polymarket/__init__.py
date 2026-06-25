from polymarket.cache.sqlite import SqliteCache
from polymarket.client.clob import CLOBClient
from polymarket.client.gamma import GammaClient
from polymarket.config import CACHE_DB_PATH, CacheTTL, IntervalSec
from polymarket.models.market import Event, Market, Token
from polymarket.models.orderbook import OrderBook, PricePoint
from polymarket.scheduler import CycleScheduler

__all__ = [
    "PolymarketClient",
    "Market", "Event", "Token",
    "OrderBook", "PricePoint",
    "CacheTTL", "IntervalMin", "IntervalSec",
    "CycleScheduler",
]


class PolymarketClient:
    """Point d'entrée principal pour interroger les APIs Polymarket (lecture seule, sans auth)."""

    def __init__(self, cache_path: str = CACHE_DB_PATH, use_cache: bool = True):
        cache = SqliteCache(cache_path) if use_cache else None
        self._gamma = GammaClient(cache=cache)
        self._clob = CLOBClient(cache=cache)
        self._cache = cache

    # --- Gamma API ---

    def get_markets(self, active: bool = True, closed: bool = False) -> list[Market]:
        """Récupère tous les marchés (pagination complète). Cache 1h."""
        return self._gamma.get_markets(active=active, closed=closed)

    def get_market(self, condition_id: str) -> Market:
        """Détail d'un marché par son condition_id. Cache 1h."""
        return self._gamma.get_market(condition_id)

    def search_markets(self, query: str, active: bool = True, closed: bool = False, ttl: int = CacheTTL.METADATA) -> list[Market]:
        """Recherche des marchés dont la question ou le slug contient query (insensible à la casse)."""
        return self._gamma.search_markets(query, active=active, closed=closed, ttl=ttl)

    def get_events(self, active: bool = True, closed: bool = False, ttl: int = CacheTTL.METADATA) -> list[Event]:
        """Récupère tous les événements (pagination complète). Cache 1h par défaut, passer CacheTTL.LIVE pour les events courts."""
        return self._gamma.get_events(active=active, closed=closed, ttl=ttl)

    # --- Enrichissement ---

    def enrich_with_prices(self, markets: list[Market], side: str = "BUY") -> None:
        """Enrichit les tokens de chaque marché avec leur prix CLOB en temps réel (modifie en place)."""
        for market in markets:
            for token in market.tokens:
                try:
                    token.price = self._clob.get_price(token.token_id, side=side)
                except Exception as e:
                    print(f"  [WARN] Prix indisponible pour {market.question[:40]!r} : {e}")

    # --- CLOB API ---

    def get_price(self, token_id: str, side: str = "BUY") -> float:
        """Prix d'un token = probabilité implicite (0–1). Cache 60s."""
        return self._clob.get_price(token_id, side=side)

    def get_orderbook(self, token_id: str) -> OrderBook:
        """Carnet d'ordres d'un token. Cache 60s."""
        return self._clob.get_orderbook(token_id)

    def get_price_history(
        self, token_id: str, interval: str = "max", fidelity: int = 100
    ) -> list[PricePoint]:
        """Historique de prix d'un token. Cache 24h.

        interval: 'max', '1d', '1w', '1m', '6m', '1y'
        fidelity: résolution en minutes
        """
        return self._clob.get_price_history(token_id, interval=interval, fidelity=fidelity)

    # --- Temps réel (bypass cache) ---

    def get_price_realtime(self, token_id: str, side: str = "BUY") -> float:
        """Prix sans cache — pour les events ultra-courts (< 1h, ex: Bitcoin ±5min)."""
        return self._clob.get_price(token_id, side=side, ttl=CacheTTL.REALTIME)

    def get_orderbook_realtime(self, token_id: str) -> OrderBook:
        """Carnet d'ordres sans cache — pour les events ultra-courts."""
        return self._clob.get_orderbook(token_id, ttl=CacheTTL.REALTIME)

    def close(self) -> None:
        self._gamma.close()
        self._clob.close()
        if self._cache:
            self._cache.close()

    def __enter__(self) -> "PolymarketClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()
