import pandas as pd

from polymarket.models.market import Market
from polymarket.models.orderbook import PricePoint


def markets_to_df(markets: list[Market]) -> pd.DataFrame:
    """Convertit une liste de marchés en DataFrame pandas."""
    rows = [
        {
            "condition_id": m.condition_id,
            "question": m.question,
            "slug": m.slug,
            "active": m.active,
            "end_date": m.end_date,
            "liquidity": m.liquidity,
            "volume": m.volume,
            "volume_24hr": m.volume_24hr,
            "best_bid": m.best_bid,
            "best_ask": m.best_ask,
            "spread": m.spread,
            "last_trade_price": m.last_trade_price,
            "outcomes": ", ".join(m.outcomes),
            "outcome_prices": ", ".join(f"{p:.2f}" for p in m.outcome_prices),
        }
        for m in markets
    ]
    return pd.DataFrame(rows)


def tokens_to_df(markets: list[Market]) -> pd.DataFrame:
    """Crée un DataFrame de tous les tokens avec leurs probabilités implicites."""
    rows = [
        {
            "condition_id": m.condition_id,
            "question": m.question,
            "token_id": token.token_id,
            "outcome": token.outcome,
            # Prix du token = probabilité implicite de l'issue (0–1)
            "implied_probability": token.price,
        }
        for m in markets
        for token in m.tokens
    ]
    return pd.DataFrame(rows)


def price_history_to_df(history: list[PricePoint]) -> pd.DataFrame:
    """Convertit un historique de prix en DataFrame avec index datetime UTC."""
    df = pd.DataFrame({"timestamp": [p.t for p in history], "price": [p.p for p in history]})
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    return df.set_index("datetime").drop(columns=["timestamp"])
