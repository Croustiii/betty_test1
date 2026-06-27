import re
import time
from datetime import datetime
from zoneinfo import ZoneInfo

_ET = ZoneInfo("America/New_York")


class MarketUtils:

    @staticmethod
    def current_5min_timestamp() -> int:
        """Retourne le timestamp Unix du début de la tranche de 5 minutes en cours."""
        return int(time.time() // 300) * 300


    @staticmethod
    def et_to_local(dt: datetime) -> datetime:
        """Convertit un datetime Eastern Time (ET) vers le fuseau horaire local du système.

        Si dt est naïf (sans tzinfo), il est considéré comme étant en ET.
        Gère automatiquement EST (UTC-5, hiver) et EDT (UTC-4, été).
        """
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=_ET)
        else:
            dt = dt.astimezone(_ET)
        return dt.astimezone()


    @staticmethod
    def localize_market_question(question: str) -> str:
        """Remplace le créneau horaire ET d'une question BTC up/down par l'heure locale.

        Exemple : 'Bitcoin Up or Down - June 25, 12:50PM-12:55PM ET'
              →   'Bitcoin Up or Down - June 25, 18:50-18:55 CEST'
        """
        pattern = r"(\d+:\d+(?:AM|PM))-(\d+:\d+(?:AM|PM)) ET"
        date_pattern = r"(\w+ \d+), " + pattern
        match = re.search(date_pattern, question)
        if not match:
            return question

        date_str, start_str, end_str = match.groups()
        year = datetime.now().year
        fmt = "%B %d %Y %I:%M%p"

        start_et = datetime.strptime(f"{date_str} {year} {start_str}", fmt)
        end_et   = datetime.strptime(f"{date_str} {year} {end_str}", fmt)

        start_local = MarketUtils.et_to_local(start_et)
        end_local   = MarketUtils.et_to_local(end_et)

        tz_name     = start_local.strftime("%Z")
        local_range = f"{start_local.strftime('%H:%M')}-{end_local.strftime('%H:%M')} {tz_name}"

        return re.sub(pattern + r"$", local_range, question)

    @staticmethod
    def get_current_btc_updown_5m_slug() -> str:
        """Retourne le slug du marché Bitcoin Up/Down correspondant à la tranche courante."""
        return f"btc-updown-5m-{MarketUtils.current_5min_timestamp()}"
