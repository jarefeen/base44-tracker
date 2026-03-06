import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from config import settings
from data_sources.base import DataSource
from utils.caching import cached

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


class SocialMentionsSource(DataSource):
    @property
    def name(self) -> str:
        return "Social Mentions"

    def is_available(self) -> bool:
        return True

    def fetch(self) -> dict:
        return _fetch_social(settings.SEARCH_TERM)


@cached(ttl_seconds=settings.CACHE_TTL_SOCIAL)
def _fetch_social(keyword: str) -> dict:
    reddit = _fetch_reddit(keyword)
    hacker_news = _fetch_hacker_news(keyword)

    all_mentions = reddit + hacker_news
    all_mentions.sort(key=lambda x: x.get("date", ""), reverse=True)

    df = pd.DataFrame(all_mentions) if all_mentions else pd.DataFrame()

    total = len(all_mentions)
    reddit_count = sum(1 for m in all_mentions if m.get("source") == "Reddit")
    hn_count = sum(1 for m in all_mentions if m.get("source") == "Hacker News")

    return {
        "df": df,
        "kpi": {
            "label": "Social Mentions",
            "value": total,
            "delta": f"Reddit: {reddit_count}, HN: {hn_count}",
        },
        "reddit_count": reddit_count,
        "hn_count": hn_count,
    }


def _fetch_reddit(keyword: str) -> list[dict]:
    """Search Reddit via their public JSON API (no auth needed)."""
    try:
        url = f"https://www.reddit.com/search.json?q={keyword}&sort=new&limit=50"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return []
        data = resp.json()
        mentions = []
        for post in data.get("data", {}).get("children", []):
            d = post.get("data", {})
            created = datetime.utcfromtimestamp(d.get("created_utc", 0))
            mentions.append({
                "source": "Reddit",
                "title": d.get("title", ""),
                "subreddit": d.get("subreddit_name_prefixed", ""),
                "score": d.get("score", 0),
                "comments": d.get("num_comments", 0),
                "date": created.strftime("%Y-%m-%d"),
                "url": f"https://reddit.com{d.get('permalink', '')}",
            })
        return mentions
    except Exception:
        return []


def _fetch_hacker_news(keyword: str) -> list[dict]:
    """Search Hacker News via Algolia API (free, no auth)."""
    try:
        url = f"https://hn.algolia.com/api/v1/search?query={keyword}&tags=story&hitsPerPage=50"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return []
        data = resp.json()
        mentions = []
        for hit in data.get("hits", []):
            mentions.append({
                "source": "Hacker News",
                "title": hit.get("title", ""),
                "subreddit": "",
                "score": hit.get("points", 0),
                "comments": hit.get("num_comments", 0),
                "date": hit.get("created_at", "")[:10],
                "url": f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
            })
        return mentions
    except Exception:
        return []
