from polymarket import PolymarketClient
from polymarket.analysis.dataframes import markets_to_df
from polymarket.config import CacheTTL
from polymarket.utils import MarketUtils


def main() -> None:
    print("Connexion aux APIs Polymarket...\n")

    with PolymarketClient() as client:
        query = "BTC"
        markets = client.search_markets(query=query, active=True, closed=False, ttl=CacheTTL.LIVE)
        print(f"  {len(markets)} marchés trouvés.\n")

        if not markets:
            print(f"  Aucun marché trouvé pour '{query}'.\n")
        else:
            client.enrich_with_prices(markets)

            df = markets_to_df(markets)
            print(f"=== Marchés correspondant à '{query}' ({len(markets)}) ===")
            print(
                df[["question", "liquidity", "volume_24hr", "best_bid", "best_ask", "spread"]]
                .to_string(max_colwidth=80)
            )
            print()


        """ Recherche du marché BTC Up/Down 5min 
        correspondant à la tranche de 5 minutes en cours """
        print("Recherche du marché BTC Up/Down 5min")

        slug = MarketUtils.get_current_btc_updown_5m_slug()
        event = client.get_event_by_slug(slug)
        print(f"=== Marché BTC Up/Down 5min (slug: '{slug}') ===")

        if not event:
            print(f"  Aucun event trouvé pour ce slug.\n")
        else:
            client.enrich_with_prices(event.markets)
            df_btc = markets_to_df(event.markets)
            print(
                df_btc[["question", "liquidity", "volume_24hr", "best_bid", "best_ask", "spread"]]
                .to_string(max_colwidth=80)
            )
            print()
            question = df_btc.loc[0, "question"]
            print(f"  Question du marché BTC Up/Down 5min:\n\t {question}\n")

            localized_question = MarketUtils.localize_market_question(question)
            print(f"  Question localisée:\n\t {localized_question}\n")

            



if __name__ == "__main__":
    main()
