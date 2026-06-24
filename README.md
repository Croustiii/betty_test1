# polymarket-client

Client Python de lecture et d'analyse de données de marché [Polymarket](https://polymarket.com).
Utilise uniquement les APIs publiques REST — aucune authentification, clé ou wallet requis.

## Prérequis

- [uv](https://docs.astral.sh/uv/) installé
- Python 3.14 (géré automatiquement par uv)

## Installation

```bash
uv sync
```

## Utilisation

### Script d'exemple

```bash
uv run examples/fetch_active_markets.py
```

### Dans du code

```python
from polymarket import PolymarketClient

with PolymarketClient() as client:
    # Marchés actifs (pagination complète, cache 1h)
    markets = client.get_markets()

    # Prix d'un token = probabilité implicite (0–1)
    price = client.get_price(token_id, side="BUY")

    # Carnet d'ordres
    book = client.get_orderbook(token_id)

    # Historique de prix
    history = client.get_price_history(token_id, interval="1m", fidelity=60)

    # Temps réel sans cache — events ultra-courts (Bitcoin ±5min, etc.)
    price_rt = client.get_price_realtime(token_id)
    book_rt  = client.get_orderbook_realtime(token_id)
```

### Analyse avec pandas

```python
from polymarket import PolymarketClient
from polymarket.analysis.dataframes import markets_to_df, tokens_to_df, price_history_to_df

with PolymarketClient() as client:
    markets = client.get_markets()
    df = markets_to_df(markets)
    print(df[["question", "liquidity", "volume_24hr", "best_bid", "best_ask"]])
```

## Cache disque

Les réponses sont mises en cache dans `polymarket_cache.db` (SQLite) avec les TTL suivants :

| Données | TTL | Méthodes |
|---|---|---|
| Temps réel (bypass) | 0s | `get_price_realtime`, `get_orderbook_realtime` |
| Prix / OrderBook | 60s | `get_price`, `get_orderbook` |
| Métadonnées marchés | 1h | `get_markets`, `get_market`, `get_events` |
| Historique de prix | 24h | `get_price_history` |

## APIs utilisées

| API | URL | Usage |
|---|---|---|
| Gamma | `https://gamma-api.polymarket.com` | Marchés, events, recherche |
| CLOB | `https://clob.polymarket.com` | Prix, orderbook, historique |

## Développement

```bash
uv run ruff check src/ examples/
uv run ruff format src/ examples/
uv run pytest
```
