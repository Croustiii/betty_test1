GAMMA_BASE_URL = "https://gamma-api.polymarket.com"
CLOB_BASE_URL = "https://clob.polymarket.com"

TIMEOUT = 15.0       # secondes par requête
RATE_LIMIT_DELAY = 0.2  # secondes entre deux appels consécutifs
PAGE_LIMIT = 100     # items par page pour la pagination
MARKET_NB_FETCH = 6 # nbre de market a récupérer

class CacheTTL:
    REALTIME = 0       # bypass total — events ultra-courts (< 1h, ex: Bitcoin ±5min)
    LIVE = 60          # prix / orderbook standard
    METADATA = 3600    # métadonnées marchés et events
    HISTORICAL = 86400  # historique de prix


CACHE_DB_PATH = "polymarket_cache.db"

