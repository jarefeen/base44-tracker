import pandas as pd

from config import settings
from data_sources.base import DataSource
from utils.caching import cached


class AppStoresSource(DataSource):
    @property
    def name(self) -> str:
        return "App Stores"

    def is_available(self) -> bool:
        return True

    def fetch(self) -> dict:
        gp = _fetch_google_play(settings.GOOGLE_PLAY_APP_ID)
        aps = _fetch_app_store(settings.APP_STORE_APP_NAME, settings.APP_STORE_APP_ID)
        return _combine(gp, aps)


@cached(ttl_seconds=settings.CACHE_TTL_APP_STORES)
def _fetch_google_play(app_id: str) -> dict | None:
    if not app_id:
        return None
    try:
        from google_play_scraper import app as gp_app
        result = gp_app(app_id)
        return {
            "store": "Google Play",
            "rating": result.get("score"),
            "ratings_count": result.get("ratings"),
            "installs": result.get("realInstalls") or result.get("installs"),
            "reviews_count": result.get("reviews"),
            "version": result.get("version"),
            "updated": result.get("updated"),
            "description": result.get("summary") or result.get("description", "")[:200],
        }
    except Exception as e:
        return {"store": "Google Play", "error": str(e)}


@cached(ttl_seconds=settings.CACHE_TTL_APP_STORES)
def _fetch_app_store(app_name: str, app_id: str) -> dict | None:
    if not app_id:
        return None
    try:
        import requests
        resp = requests.get(
            f"https://itunes.apple.com/lookup?id={app_id}&country=us",
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return {"store": "App Store", "error": "App not found"}
        r = results[0]
        return {
            "store": "App Store",
            "rating": r.get("averageUserRating"),
            "ratings_count": r.get("userRatingCount"),
            "version": r.get("version"),
            "description": (r.get("description") or "")[:200],
        }
    except Exception as e:
        return {"store": "App Store", "error": str(e)}


def _combine(gp: dict | None, aps: dict | None) -> dict:
    rows = []
    best_rating = None

    for store_data in [gp, aps]:
        if store_data is None:
            continue
        if "error" in store_data:
            rows.append(store_data)
            continue
        rows.append(store_data)
        rating = store_data.get("rating")
        if rating is not None:
            best_rating = rating if best_rating is None else max(best_rating, rating)

    df = pd.DataFrame(rows) if rows else pd.DataFrame()

    if not rows or all("error" in r for r in rows if r):
        kpi = {"label": "App Rating", "value": "N/A", "delta": "Not on stores yet"}
    else:
        kpi = {
            "label": "App Rating",
            "value": f"{best_rating:.1f}" if best_rating else "N/A",
            "delta": None,
        }

    return {"df": df, "kpi": kpi}
