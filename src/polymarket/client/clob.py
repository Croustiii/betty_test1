from polymarket.cache.sqlite import SqliteCache
from polymarket.client.base import HttpClient
from polymarket.config import CLOB_BASE_URL, CacheTTL
from polymarket.models.orderbook import OrderBook, PricePoint


class CLOBClient:
    def __init__(self, cache: SqliteCache | None = None):
        self._http = HttpClient(base_url=CLOB_BASE_URL, cache=cache)

    def get_price(self, token_id: str, side: str = "BUY", ttl: int = CacheTTL.LIVE) -> float:
        """Prix d'un token = probabilité implicite de l'issue (0–1).

        side: 'BUY' ou 'SELL'
        ttl=0 pour bypass cache (events ultra-courts).
        """
        data = self._http.get("/price", {"token_id": token_id, "side": side}, ttl=ttl)
        return float(data["price"])

    def get_orderbook(self, token_id: str, ttl: int = CacheTTL.LIVE) -> OrderBook:
        """Carnet d'ordres complet d'un token."""
        data = self._http.get("/book", {"token_id": token_id}, ttl=ttl)
        return OrderBook.model_validate(data)

    def get_price_history(
        self,
        token_id: str,
        interval: str = "max",
        fidelity: int = 100,
        ttl: int = CacheTTL.HISTORICAL,
    ) -> list[PricePoint]:
        """Historique de prix d'un token (probabilités implicites dans le temps).

        interval: 'max', '1d', '1w', '1m', '6m', '1y'
        fidelity: résolution en minutes
        """
        data = self._http.get(
            "/prices-history",
            {"market": token_id, "interval": interval, "fidelity": fidelity},
            ttl=ttl,
        )
        return [PricePoint.model_validate(p) for p in data["history"]]

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "CLOBClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()
