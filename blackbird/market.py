from polygon import RESTClient
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
import random
from database import write_market, read_market
from functools import lru_cache

load_dotenv(override=True)
polygon_api_key = os.getenv("POLYGON_API_KEY")


def is_market_open() -> bool:
    if not polygon_api_key:
        return False
    client = RESTClient(polygon_api_key)
    try:
        market_status = client.get_market_status()
        return market_status.market == "open"
    except Exception:
        return False


def get_all_share_prices_polygon_eod() -> dict[str, float]:
    client = RESTClient(polygon_api_key)
    probe = client.get_previous_close_agg("SPY")[0]
    last_close_date = datetime.fromtimestamp(probe.timestamp / 1000, tz=timezone.utc).date()
    results = client.get_grouped_daily_aggs(date=last_close_date, adjusted=True, include_otc=False)
    return {item.ticker: item.close for item in results}


@lru_cache(maxsize=2)
def get_market_for_prior_date(cache_key):
    market_data = read_market(cache_key)
    if not market_data:
        market_data = get_all_share_prices_polygon_eod()
        write_market(cache_key, market_data)
    return market_data


def get_share_price(symbol: str) -> float:
    if not polygon_api_key:
        return float(random.randint(100, 10000)) / 100

    try:
        today_str = datetime.now().date().strftime("%Y-%m-%d")
        market_data = get_market_for_prior_date(today_str)
        price = market_data.get(symbol.upper())
        return price if price is not None else 0.0
    except Exception:
        return float(random.randint(100, 10000)) / 100