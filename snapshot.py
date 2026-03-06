"""Standalone script to record daily snapshots. Run via GitHub Actions or cron."""
import json
import os
import sys
from datetime import date
from pathlib import Path

import requests

HISTORY_FILE = Path(__file__).resolve().parent / "cache" / "history.json"
GOOGLE_PLAY_APP_ID = os.getenv("GOOGLE_PLAY_APP_ID", "com.base44.android")
APP_STORE_APP_ID = os.getenv("APP_STORE_APP_ID", "6749351042")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
SEARCH_TERM = "base44"


def load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_history(data: dict):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(data, indent=2))


def record(source: str, metrics: dict, data: dict):
    today = date.today().isoformat()
    if source not in data:
        data[source] = {}
    data[source][today] = metrics
    print(f"  {source}: {metrics}")


def fetch_youtube(api_key: str) -> dict | None:
    if not api_key:
        print("  Skipping YouTube (no API key)")
        return None
    from googleapiclient.discovery import build
    yt = build("youtube", "v3", developerKey=api_key)
    search = yt.search().list(q=SEARCH_TERM, part="snippet", type="video", maxResults=20, order="relevance").execute()
    video_ids = [item["id"]["videoId"] for item in search.get("items", [])]
    if not video_ids:
        return {"total_views": 0, "video_count": 0}
    stats = yt.videos().list(id=",".join(video_ids), part="statistics").execute()
    total_views = sum(int(item.get("statistics", {}).get("viewCount", 0)) for item in stats.get("items", []))
    return {"total_views": total_views, "video_count": len(video_ids)}


def fetch_google_play(app_id: str) -> dict | None:
    if not app_id:
        return None
    from google_play_scraper import app as gp_app
    result = gp_app(app_id)
    return {
        "google_play_rating": round(result.get("score", 0), 2),
        "google_play_ratings_count": result.get("ratings", 0),
        "google_play_installs": result.get("realInstalls", 0),
    }


def fetch_app_store(app_id: str) -> dict | None:
    if not app_id:
        return None
    resp = requests.get(f"https://itunes.apple.com/lookup?id={app_id}&country=us", timeout=10)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        return None
    r = results[0]
    return {
        "app_store_rating": round(r.get("averageUserRating", 0), 2),
        "app_store_ratings_count": r.get("userRatingCount", 0),
    }


def main():
    print(f"Recording snapshots for {date.today().isoformat()}")
    data = load_history()

    # YouTube
    print("Fetching YouTube...")
    try:
        yt = fetch_youtube(YOUTUBE_API_KEY)
        if yt:
            record("youtube", yt, data)
    except Exception as e:
        print(f"  YouTube error: {e}")

    # App Stores
    print("Fetching App Stores...")
    app_store_snapshot = {}
    try:
        gp = fetch_google_play(GOOGLE_PLAY_APP_ID)
        if gp:
            app_store_snapshot.update(gp)
    except Exception as e:
        print(f"  Google Play error: {e}")

    try:
        aps = fetch_app_store(APP_STORE_APP_ID)
        if aps:
            app_store_snapshot.update(aps)
    except Exception as e:
        print(f"  App Store error: {e}")

    if app_store_snapshot:
        record("app_stores", app_store_snapshot, data)

    save_history(data)
    print("Done. History saved.")


if __name__ == "__main__":
    main()
