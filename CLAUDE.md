# Base44 Traction Tracker

## Project Overview
Streamlit dashboard tracking Base44 traction metrics across 3 data sources: Google Trends, YouTube, and App Stores.

## Project Location
- Files are written to `C:\Users\jarefeen\base44-tracker` but the runtime/venv lives on `H:\base44-tracker`
- After editing files, sync to H: before restarting: `cp "C:\\Users\\jarefeen\\base44-tracker/<file>" /h/base44-tracker/<file>`
- Always kill ALL old streamlit processes before restarting: `taskkill //F //IM streamlit.exe`

## Running
```bash
cd /h/base44-tracker && /h/base44-tracker/.venv/Scripts/streamlit.exe run app.py --server.headless true
```
Dashboard at http://localhost:8501

## Key Architecture
- **Data sources** (`data_sources/`): Each implements `DataSource` base class with `fetch_safe()` error boundary
- **Two-level caching**: `st.cache_data` (in-memory) + `diskcache` (persistent in `cache/` dir)
- **Graceful degradation**: Unconfigured sources show info messages, not errors
- All sources optional — Google Trends + App Stores need no API keys

## Environment
- `.env` holds API keys (gitignored). `.env.example` has the template.
- `truststore` is injected at startup for corporate proxy SSL compatibility
- `urllib3<2` is pinned because `pytrends` uses deprecated `method_whitelist` kwarg

## App Store IDs
- Google Play: `com.base44.android`
- App Store: ID `6749351042` (via iTunes Lookup API — `app-store-scraper` library is broken)

## Data Sources
| Source | API Key | Cache TTL | Module |
|--------|---------|-----------|--------|
| Google Trends | None | 4h | `data_sources/google_trends.py` |
| YouTube | `YOUTUBE_API_KEY` | 1h | `data_sources/youtube.py` |
| App Stores | None | 2h | `data_sources/app_stores.py` |

## Known Issues
- `pytrends` rate limits aggressively (429 errors) — 4h cache TTL mitigates this
- `app-store-scraper` pip package is broken; App Store data uses iTunes Lookup API directly instead
- Website traffic source was removed (all free APIs are paid or unreliable)
