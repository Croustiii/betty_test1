import json
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Token(BaseModel):
    token_id: str
    outcome: str
    # Prix du token = probabilité implicite de l'issue (0 = impossible, 1 = certain)
    price: float | None = None


class Market(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str
    condition_id: str = Field(validation_alias="conditionId")
    question: str
    slug: str
    active: bool
    closed: bool
    end_date: datetime | None = Field(None, validation_alias="endDate")
    start_date: datetime | None = Field(None, validation_alias="startDate")
    liquidity: float = 0.0
    volume: float = 0.0
    volume_24hr: float | None = Field(None, validation_alias="volume24hr")
    volume_1wk: float | None = Field(None, validation_alias="volume1wk")
    volume_1mo: float | None = Field(None, validation_alias="volume1mo")
    outcomes: list[str] = Field(default_factory=list)
    outcome_prices: list[float] = Field(default_factory=list, validation_alias="outcomePrices")
    token_ids: list[str] = Field(default_factory=list, validation_alias="clobTokenIds")
    best_bid: float | None = Field(None, validation_alias="bestBid")
    best_ask: float | None = Field(None, validation_alias="bestAsk")
    last_trade_price: float | None = Field(None, validation_alias="lastTradePrice")
    spread: float | None = None
    enable_order_book: bool = Field(True, validation_alias="enableOrderBook")
    tokens: list[Token] = Field(default_factory=list)

    @field_validator("outcomes", "outcome_prices", "token_ids", mode="before")
    @classmethod
    def parse_json_string(cls, v: object) -> object:
        if isinstance(v, str):
            return json.loads(v)
        return v

    @model_validator(mode="after")
    def build_tokens(self) -> "Market":
        if self.outcomes and self.token_ids:
            prices = self.outcome_prices or [None] * len(self.outcomes)
            self.tokens = [
                Token(
                    token_id=tid,
                    outcome=outcome,
                    price=float(price) if price is not None else None,
                )
                for outcome, tid, price in zip(self.outcomes, self.token_ids, prices)
            ]
        return self


class Event(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str
    slug: str
    title: str
    ticker: str | None = None
    active: bool
    closed: bool
    end_date: datetime | None = Field(None, validation_alias="endDate")
    start_date: datetime | None = Field(None, validation_alias="startDate")
    liquidity: float = 0.0
    volume: float = 0.0
    volume_24hr: float | None = Field(None, validation_alias="volume24hr")
    markets: list[Market] = Field(default_factory=list)
    tags: list[dict] = Field(default_factory=list)
