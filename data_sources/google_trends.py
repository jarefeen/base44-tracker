import time
import pandas as pd
import requests
from pytrends.request import TrendReq

from config import settings
from data_sources.base import DataSource
from utils.caching import cached

# Use OS trust store to handle corporate proxies / self-signed certs
try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass


def _make_session() -> requests.Session:
    session = requests.Session()
    session.verify = True
    return session


class GoogleTrendsSource(DataSource):
    @property
    def name(self) -> str:
        return "Google Trends"

    def is_available(self) -> bool:
        return True

    def fetch(self) -> dict:
        data = _fetch_trends(settings.SEARCH_TERM)
        data["comparison"] = _fetch_comparison(
            settings.SEARCH_TERM, tuple(settings.COMPETITORS)
        )
        return data


@cached(ttl_seconds=settings.CACHE_TTL_GOOGLE_TRENDS)
def _fetch_trends(keyword: str) -> dict:
    pytrends = TrendReq(hl="en-US", tz=360, retries=3, backoff_factor=2,
                        requests_args={"verify": True})
    pytrends.build_payload([keyword], cat=0, timeframe="today 3-m")

    # Interest over time
    iot = pytrends.interest_over_time()
    if iot.empty:
        return {
            "df": pd.DataFrame(),
            "kpi": {"label": "Trend Score", "value": 0, "delta": None},
            "related_queries": pd.DataFrame(),
        }

    iot = iot.reset_index()
    if "isPartial" in iot.columns:
        iot = iot.drop(columns=["isPartial"])

    # Compute KPI: latest value and delta vs previous week
    latest = int(iot[keyword].iloc[-1])
    previous = int(iot[keyword].iloc[-2]) if len(iot) > 1 else None
    delta = None
    if previous and previous > 0:
        delta = f"{((latest - previous) / previous) * 100:+.1f}%"

    # Related queries
    try:
        related = pytrends.related_queries()
        rq = related.get(keyword, {}).get("rising", pd.DataFrame())
        if rq is None:
            rq = pd.DataFrame()
    except Exception:
        rq = pd.DataFrame()

    return {
        "df": iot,
        "kpi": {"label": "Trend Score", "value": latest, "delta": delta},
        "related_queries": rq,
    }


@cached(ttl_seconds=settings.CACHE_TTL_GOOGLE_TRENDS)
def _fetch_comparison(keyword: str, competitors: tuple) -> pd.DataFrame:
    """Fetch interest over time for keyword vs competitors on the same scale."""
    all_terms = [keyword] + list(competitors)
    # pytrends allows max 5 terms per request
    all_terms = all_terms[:5]
    try:
        pytrends = TrendReq(hl="en-US", tz=360, retries=3, backoff_factor=2,
                            requests_args={"verify": True})
        pytrends.build_payload(all_terms, cat=0, timeframe="today 3-m")
        df = pytrends.interest_over_time()
        if df.empty:
            return pd.DataFrame()
        df = df.reset_index()
        if "isPartial" in df.columns:
            df = df.drop(columns=["isPartial"])
        return df
    except Exception:
        return pd.DataFrame()
