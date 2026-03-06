import pandas as pd

from config import settings
from data_sources.base import DataSource
from utils.caching import cached
from utils.formatting import abbreviate_number


class YouTubeSource(DataSource):
    @property
    def name(self) -> str:
        return "YouTube"

    def is_available(self) -> bool:
        return bool(settings.YOUTUBE_API_KEY)

    def fetch(self) -> dict:
        if not self.is_available():
            return {
                "df": pd.DataFrame(),
                "kpi": {"label": "YouTube Views", "value": "N/A", "delta": "No API key"},
            }
        return _fetch_youtube(settings.SEARCH_TERM, settings.YOUTUBE_API_KEY)


@cached(ttl_seconds=settings.CACHE_TTL_YOUTUBE)
def _fetch_youtube(keyword: str, api_key: str) -> dict:
    from googleapiclient.discovery import build

    youtube = build("youtube", "v3", developerKey=api_key)

    # Search for videos about Base44 (costs 100 quota units)
    search_resp = youtube.search().list(
        q=keyword, part="snippet", type="video", maxResults=20, order="relevance"
    ).execute()

    video_ids = [item["id"]["videoId"] for item in search_resp.get("items", [])]

    if not video_ids:
        return {
            "df": pd.DataFrame(),
            "kpi": {"label": "YouTube Views", "value": 0, "delta": "No videos found"},
        }

    # Get video statistics (costs 1 unit per call)
    stats_resp = youtube.videos().list(
        id=",".join(video_ids), part="snippet,statistics"
    ).execute()

    rows = []
    total_views = 0
    for item in stats_resp.get("items", []):
        snippet = item["snippet"]
        stats = item.get("statistics", {})
        views = int(stats.get("viewCount", 0))
        total_views += views
        rows.append({
            "title": snippet["title"],
            "channel": snippet["channelTitle"],
            "published": snippet["publishedAt"][:10],
            "views": views,
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "video_id": item["id"],
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("views", ascending=False).reset_index(drop=True)

    return {
        "df": df,
        "kpi": {
            "label": "YouTube Views",
            "value": abbreviate_number(total_views),
            "delta": f"{len(rows)} videos found",
        },
        "total_views": total_views,
        "video_count": len(rows),
    }
