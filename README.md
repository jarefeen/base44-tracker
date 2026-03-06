# Base44 Traction Tracker

Real-time dashboard tracking Base44 traction metrics across Google Trends, website traffic, YouTube, and app stores.

## Quick Start

```bash
cd base44-tracker
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys (optional - dashboard works without any keys)

streamlit run app.py
```

Dashboard opens at http://localhost:8501

## Data Sources

| Source | API Key Required | Cache TTL |
|--------|-----------------|-----------|
| Google Trends | No | 4 hours |
| App Stores | No | 2 hours |
| YouTube | Yes (free) | 1 hour |
| Website Traffic | Optional | 6 hours |

## Getting a YouTube API Key (Free)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Navigate to **APIs & Services > Library**
4. Search for and enable **YouTube Data API v3**
5. Go to **Credentials > Create Credentials > API Key**
6. Copy the key into `.env` as `YOUTUBE_API_KEY=your_key_here`

Free tier provides 10,000 quota units/day (~100 searches/day).

## Finding App Store IDs

**Google Play:** Search `https://play.google.com/store/search?q=base44` and extract the package name from the URL (e.g., `com.base44.app`). Set as `GOOGLE_PLAY_APP_ID` in `.env`.

**App Store:** Search `https://apps.apple.com/search?term=base44`. Set the app name and numeric ID in `.env`.

## Project Structure

```
base44-tracker/
├── app.py                  # Main Streamlit entrypoint
├── config/settings.py      # Central configuration
├── data_sources/           # One module per data source
├── components/             # Reusable UI components
├── utils/                  # Caching, formatting helpers
└── cache/                  # Persistent disk cache (gitignored)
```
