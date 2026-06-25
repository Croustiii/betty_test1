import httpx

from polymarket.cache.sqlite import SqliteCache
from polymarket.client.base import HttpClient
from polymarket.config import GAMMA_BASE_URL, PAGE_LIMIT, CacheTTL
from polymarket.models.market import Event, Market


class GammaClient:
    def __init__(self, cache: SqliteCache | None = None):
        self._http = HttpClient(base_url=GAMMA_BASE_URL, cache=cache)

    def get_markets(
        self,
        active: bool = True,
        closed: bool = False,
        ttl: int = CacheTTL.METADATA,
    ) -> list[Market]:
        """Récupère tous les marchés avec pagination complète."""
        results: list[dict] = []
        offset = 0
        while True:
            params = {
                "active": str(active).lower(),
                "closed": str(closed).lower(),
                "limit": PAGE_LIMIT,
                "offset": offset,
            }
            try:
                page = self._http.get("/markets", params, ttl=ttl)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 422:
                    break  # offset dépassé — fin de la pagination
                raise
            if not page:
                break
            results.extend(page)
            if len(page) < PAGE_LIMIT:
                break
            offset += PAGE_LIMIT
        return [Market.model_validate(m) for m in results]

    def search_markets(
        self,
        query: str,
        active: bool = True,
        closed: bool = False,
        ttl: int = CacheTTL.METADATA,
    ) -> list[Market]:
        """Retourne les marchés dont la question contient query (insensible à la casse)."""
        q = query.lower()
        return [m for m in self.get_markets(active=active, closed=closed, ttl=ttl)
                if q in m.question.lower() or q in m.slug.lower()]

    def get_market(self, condition_id: str, ttl: int = CacheTTL.METADATA) -> Market:
        """Détail d'un marché par son condition_id."""
        data = self._http.get(f"/markets/{condition_id}", ttl=ttl)
        if isinstance(data, list):
            data = data[0]
        return Market.model_validate(data)

    def get_events(
        self,
        active: bool = True,
        closed: bool = False,
        ttl: int = CacheTTL.METADATA,
    ) -> list[Event]:
        """Récupère tous les événements avec pagination complète."""
        results: list[dict] = []
        offset = 0
        while True:
            params = {
                "active": str(active).lower(),
                "closed": str(closed).lower(),
                "limit": PAGE_LIMIT,
                "offset": offset,
            }
            try:
                page = self._http.get("/events", params, ttl=ttl)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 422:
                    break  # offset dépassé — fin de la pagination
                raise
            if not page:
                break
            results.extend(page)
            if len(page) < PAGE_LIMIT:
                break
            offset += PAGE_LIMIT
        return [Event.model_validate(e) for e in results]

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "GammaClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()
