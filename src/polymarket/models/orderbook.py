from pydantic import BaseModel, ConfigDict


class OrderLevel(BaseModel):
    price: float
    size: float


class OrderBook(BaseModel):
    model_config = ConfigDict(extra="ignore")

    market: str    # condition_id
    asset_id: str  # token_id
    timestamp: int
    bids: list[OrderLevel]
    asks: list[OrderLevel]

    @property
    def best_bid(self) -> float | None:
        return max((b.price for b in self.bids), default=None)

    @property
    def best_ask(self) -> float | None:
        return min((a.price for a in self.asks), default=None)

    @property
    def spread(self) -> float | None:
        bid, ask = self.best_bid, self.best_ask
        if bid is not None and ask is not None:
            return round(ask - bid, 4)
        return None


class PricePoint(BaseModel):
    """Point d'historique de prix. p = probabilité implicite de l'issue (0–1)."""

    t: int    # Unix timestamp
    p: float  # prix implicite = probabilité implicite (0–1)
