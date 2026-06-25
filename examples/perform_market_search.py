from polymarket import PolymarketClient
from polymarket.analysis.dataframes import markets_to_df
from polymarket.config import CacheTTL


def main() -> None:
    print("Connexion aux APIs Polymarket...\n")

    with PolymarketClient() as client:
        query = "BTC"
        markets = client.search_markets(query=query, active=True, closed=False, ttl=CacheTTL.LIVE)
        print(f"  {len(markets)} marchés trouvés.\n")

        if not markets:
            print(f"Aucun marché trouvé pour '{query}'.")
            return

        client.enrich_with_prices(markets)

        df = markets_to_df(markets)
        print(f"=== Marchés correspondant à '{query}' ({len(markets)}) ===")
        print(
            df[["question", "liquidity", "volume_24hr", "best_bid", "best_ask", "spread"]]
            .to_string(max_colwidth=80)
        )
        print()


if __name__ == "__main__":
    main()
