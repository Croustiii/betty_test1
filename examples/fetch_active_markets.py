"""
Exemple : liste des marchés actifs, récupération des prix CLOB, analyse en DataFrame.
Usage : uv run examples/fetch_active_markets.py
"""

from polymarket import PolymarketClient
from polymarket.analysis.dataframes import markets_to_df, price_history_to_df, tokens_to_df
from polymarket.config import MARKET_NB_FETCH, CacheTTL
from polymarket.storage.events import EventStore

def main() -> None:
    print("Connexion aux APIs Polymarket...\n")

    with PolymarketClient() as client:
        # 1. Récupérer les marchés actifs (pagination complète, cache 1h)
        print("Récupération des marchés actifs...")
        markets = client.get_markets(active=True, closed=False)
        print(f"  {len(markets)} marches recuperes.\n")

        # 2. Enrichir les 5 premiers marchés avec les prix CLOB en temps réel
        print(f"Récupération des prix CLOB ({MARKET_NB_FETCH} premiers marchés)...")
        client.enrich_with_prices(markets[:MARKET_NB_FETCH])
        print()

        # 3. DataFrame des marchés
        df_markets = markets_to_df(markets[:MARKET_NB_FETCH])
        pd_opts = {"max_colwidth": 80, "max_rows": MARKET_NB_FETCH}
        print(f'=== Marchés actifs ({MARKET_NB_FETCH} premiers) ===')
        print(
            df_markets[["question", "liquidity", "volume_24hr", "best_bid", "best_ask", "spread"]]
            .to_string(**pd_opts)
        )
        print()

        # 4. DataFrame des tokens avec probabilités implicites
        df_tokens = tokens_to_df(markets[:MARKET_NB_FETCH])
        print(f"=== Tokens — probabilités implicites ({MARKET_NB_FETCH} premiers marchés) ===")
        print(df_tokens[["question", "outcome", "implied_probability"]].to_string(max_colwidth=50))
        print()

        # 5. Liste des événements actifs + persistance SQLite
        print("Récupération des événements actifs...")
        events = client.get_events(active=True, closed=False, ttl=CacheTTL.LIVE)
        print(f"  {len(events)} événements récupérés.")

        with EventStore() as store:
            nb = store.upsert(events)
            print(f"  {nb} événements stockés dans la table 'events' (polymarket_cache.db). Total en base : {store.count()}\n")

        print(f"=== Événements actifs ({min(10, len(events))} premiers) ===")
        for event in events[:10]:
            print(f"  [{event.end_date.date() if event.end_date else 'N/A'}] {event.title}")
            vol = f"{event.volume_24hr:,.0f} $" if event.volume_24hr is not None else "N/A"
            print(f"    Marchés : {len(event.markets)} | Volume 24h : {vol} | Liquidité : {event.liquidity:,.0f} $")
            for market in event.markets[:3]:
                probs = " / ".join(
                    f"{t.outcome} {t.price:.0%}" for t in market.tokens if t.price is not None
                )
                print(f"    → {market.question[:70]} {f'({probs})' if probs else ''}")
            if len(event.markets) > 3:
                print(f"    … et {len(event.markets) - 3} autre(s) marché(s)")
        print()

        # 6. Historique de prix pour le premier token disponible
        if markets and markets[0].tokens:
            first_market = markets[0]
            first_token = first_market.tokens[0]
            print(f"=== Historique de prix : {first_market.question[:60]} ===")
            history = client.get_price_history(first_token.token_id, interval="1m", fidelity=60)
            print(f"  {len(history)} points récupérés.")
            if history:
                df_hist = price_history_to_df(history)
                print(df_hist.tail(5).to_string())
            print()


if __name__ == "__main__":
    main()
