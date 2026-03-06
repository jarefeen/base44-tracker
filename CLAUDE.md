# Base44 Traction Tracker

## Project Location (critical)
- Write tool saves to `C:\Users\jarefeen\base44-tracker`, but venv/runtime is on `H:\base44-tracker`
- **Always sync edited files to H: before restarting**: `cp "C:\\Users\\jarefeen\\base44-tracker/<file>" /h/base44-tracker/<file>`
- **Always kill ALL old streamlit processes**: `taskkill //F //IM streamlit.exe` (multiple can accumulate)

## Running
```bash
cd /h/base44-tracker && /h/base44-tracker/.venv/Scripts/streamlit.exe run app.py --server.headless true
```

## Key Gotchas
- `truststore` must be injected at startup for corporate proxy SSL
- `urllib3<2` pinned — `pytrends` uses removed `method_whitelist` kwarg in urllib3 2.x
- `app-store-scraper` pip package is broken — use iTunes Lookup API (`itunes.apple.com/lookup`) instead
- `YOUTUBE_API_KEY` must be a `@property` in Settings (lazy read) so Streamlit Cloud secrets work
- `.env` is gitignored — app store IDs are hardcoded as defaults in `settings.py` for Streamlit Cloud
- Google Trends competitor terms must be specific (e.g., `bubble.io` not `bubble`, `lovable.dev` not `lovable`) to avoid common-word noise
- `pytrends` rate limits aggressively — 4h cache TTL mitigates this

## Architecture
- Data sources in `data_sources/` each implement `DataSource` base class with `fetch_safe()` error boundary
- Two-level caching: `st.cache_data` (in-memory) + `diskcache` (persistent)
- Historical tracking: `utils/history.py` saves daily snapshots to `cache/history.json`
- GitHub Actions (`daily-snapshot.yml`) runs `snapshot.py` at 8AM UTC to record data without anyone visiting

## Deployment
- GitHub repo: `jarefeen/base44-tracker`
- Streamlit Cloud auto-deploys on push to master
- YouTube API key must be added in Streamlit Cloud Settings > Secrets
