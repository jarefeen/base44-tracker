import streamlit as st
import pandas as pd

# Inject OS trust store for corporate proxy/self-signed cert environments
try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

from config import settings
from data_sources.google_trends import GoogleTrendsSource
from data_sources.app_stores import AppStoresSource
from data_sources.youtube import YouTubeSource
from components.kpi_card import render_kpi_card
from components.trend_chart import render_line_chart, render_bar_chart
from components.status_banner import render_status_banner
from utils.caching import clear_all_cache
from utils.history import record_snapshot, get_history

st.set_page_config(
    page_title=f"{settings.SEARCH_TERM_DISPLAY} Traction Tracker",
    page_icon="📈",
    layout="wide",
)

# --- Initialize data sources ---
sources = {
    "google_trends": GoogleTrendsSource(),
    "youtube": YouTubeSource(),
    "app_stores": AppStoresSource(),
}

# --- Sidebar ---
with st.sidebar:
    st.title("📈 Traction Tracker")
    st.caption(f"Tracking: **{settings.SEARCH_TERM_DISPLAY}**")
    st.divider()

    st.subheader("Data Sources")
    enabled = {}
    for key, src in sources.items():
        available = src.is_available()
        label = f"{src.name} {'✓' if available else '(not configured)'}"
        enabled[key] = st.checkbox(label, value=available, disabled=not available)

    st.divider()
    if st.button("🔄 Refresh All Data", use_container_width=True):
        clear_all_cache()
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.subheader("API Keys")
    st.caption("Configure in `.env` file")
    for key_name, present in [
        ("YOUTUBE_API_KEY", bool(settings.YOUTUBE_API_KEY)),
    ]:
        icon = "✅" if present else "❌"
        st.text(f"{icon} {key_name}")

# --- Fetch data ---
@st.cache_data(ttl=300, show_spinner="Fetching data...")
def fetch_all(enabled_keys: tuple) -> dict:
    results = {}
    for key in enabled_keys:
        results[key] = sources[key].fetch_safe()
    return results

enabled_keys = tuple(k for k, v in enabled.items() if v)
results = fetch_all(enabled_keys)

# --- Record daily snapshots for historical tracking ---
r_yt = results.get("youtube")
if r_yt and r_yt.get("ok") and r_yt.get("total_views") is not None:
    record_snapshot("youtube", {
        "total_views": r_yt["total_views"],
        "video_count": r_yt.get("video_count", 0),
    })

r_as = results.get("app_stores")
if r_as and r_as.get("ok") and not r_as["df"].empty:
    snapshot = {}
    for _, row in r_as["df"].iterrows():
        store = row.get("store", "").replace(" ", "_").lower()
        if "error" in row and pd.notna(row.get("error")):
            continue
        if pd.notna(row.get("rating")):
            snapshot[f"{store}_rating"] = round(float(row["rating"]), 2)
        if pd.notna(row.get("ratings_count")):
            snapshot[f"{store}_ratings_count"] = int(row["ratings_count"])
        if pd.notna(row.get("installs")):
            snapshot[f"{store}_installs"] = int(row["installs"])
    if snapshot:
        record_snapshot("app_stores", snapshot)

# --- Header ---
st.title(f"{settings.SEARCH_TERM_DISPLAY} Traction Tracker")

# --- Status banner ---
status_list = []
for key, src in sources.items():
    r = results.get(key)
    status_list.append({
        "name": src.name,
        "available": src.is_available(),
        "ok": r["ok"] if r else False,
    })
render_status_banner(status_list)
st.divider()

# --- KPI Row ---
kpi_cols = st.columns(3)
kpi_order = ["google_trends", "youtube", "app_stores"]
for col, key in zip(kpi_cols, kpi_order):
    r = results.get(key)
    with col:
        if r and r.get("kpi"):
            kpi = r["kpi"]
            render_kpi_card(kpi["label"], kpi["value"], kpi.get("delta"))
        else:
            src = sources[key]
            msg = settings.get_missing_key_message(key)
            render_kpi_card(src.name, "—", msg or "Disabled")

st.divider()

# --- Tabs ---
tab_names = ["Google Trends", "YouTube", "App Stores"]
tabs = st.tabs(tab_names)

# -- Google Trends tab --
with tabs[0]:
    r = results.get("google_trends")
    if r and r["ok"]:
        df = r["df"]
        if not df.empty:
            st.caption(
                "**How to read this:** The score is relative search interest on a 0-100 scale. "
                "100 = peak popularity in the time period, 50 = half the peak. "
                "It's not absolute search volume. Watch for upward trends (growing awareness), "
                "spikes (launches/press coverage), or steady declines (losing mindshare)."
            )
            render_line_chart(df, x="date", y=settings.SEARCH_TERM, title="Interest Over Time (past 3 months)")

            related = r.get("related_queries")
            if related is not None and not related.empty:
                st.subheader("Rising Related Queries")
                st.dataframe(related, use_container_width=True, hide_index=True)
        else:
            st.info(f"No Google Trends data found for '{settings.SEARCH_TERM}'. The term may be too new or niche.")
    elif r:
        st.error(f"Error fetching Google Trends: {r.get('error')}")
    else:
        st.info("Google Trends is disabled. Enable it in the sidebar.")

# -- YouTube tab --
with tabs[1]:
    r = results.get("youtube")
    if r and r["ok"]:
        df = r["df"]
        if not df.empty:
            st.subheader(f"Top Videos ({r.get('video_count', len(df))} found)")
            render_bar_chart(
                df.head(10), x="title", y="views",
                title="Views by Video", horizontal=True
            )
            st.dataframe(
                df[["title", "channel", "published", "views", "likes", "comments"]],
                use_container_width=True,
                hide_index=True,
            )

        # Historical tracking
        yt_history = get_history("youtube")
        if len(yt_history) > 1:
            st.subheader("Engagement Over Time")
            st.caption("Tracked daily — total views and video count each time the dashboard loads.")
            hist_df = pd.DataFrame(yt_history)
            render_line_chart(hist_df, x="date", y="total_views", title="Total YouTube Views Over Time")
            render_line_chart(hist_df, x="date", y="video_count", title="Number of Videos Over Time")
        elif len(yt_history) == 1:
            st.info("Historical tracking started. Come back tomorrow to see trends over time.")
        else:
            st.info(f"No YouTube videos found for '{settings.SEARCH_TERM}'.")
    elif r:
        st.error(f"Error fetching YouTube data: {r.get('error')}")
    else:
        if not settings.YOUTUBE_API_KEY:
            st.info("YouTube tracking requires an API key.\n\n"
                    "**Setup:**\n"
                    "1. Go to [Google Cloud Console](https://console.cloud.google.com)\n"
                    "2. Enable YouTube Data API v3\n"
                    "3. Create an API key\n"
                    "4. Add `YOUTUBE_API_KEY=your_key` to `.env`")
        else:
            st.info("YouTube is disabled. Enable it in the sidebar.")

# -- App Stores tab --
with tabs[2]:
    r = results.get("app_stores")
    if r and r["ok"]:
        df = r["df"]
        if not df.empty:
            if "error" in df.columns and df["error"].notna().any():
                for _, row in df[df["error"].notna()].iterrows():
                    st.warning(f"{row.get('store', 'Store')}: {row['error']}")
                df_clean = df[df["error"].isna()] if "error" in df.columns else df
            else:
                df_clean = df

            if not df_clean.empty:
                st.dataframe(df_clean, use_container_width=True, hide_index=True)

                # Historical tracking
                as_history = get_history("app_stores")
                if len(as_history) > 1:
                    st.subheader("Engagement Over Time")
                    st.caption("Tracked daily — ratings and installs each time the dashboard loads.")
                    hist_df = pd.DataFrame(as_history)
                    if "google_play_installs" in hist_df.columns:
                        render_line_chart(hist_df, x="date", y="google_play_installs", title="Google Play Installs Over Time")
                    rating_cols = [c for c in hist_df.columns if c.endswith("_rating")]
                    if rating_cols:
                        for col in rating_cols:
                            label = col.replace("_", " ").replace(" rating", "").title()
                            render_line_chart(hist_df, x="date", y=col, title=f"{label} Rating Over Time")
                    count_cols = [c for c in hist_df.columns if c.endswith("_ratings_count")]
                    if count_cols:
                        for col in count_cols:
                            label = col.replace("_", " ").replace(" ratings count", "").title()
                            render_line_chart(hist_df, x="date", y=col, title=f"{label} Ratings Count Over Time")
                elif len(as_history) == 1:
                    st.info("Historical tracking started. Come back tomorrow to see trends over time.")
            else:
                st.info(f"'{settings.SEARCH_TERM_DISPLAY}' not found on app stores yet. "
                        "Configure app IDs in `.env` when available.")
        else:
            st.info(f"'{settings.SEARCH_TERM_DISPLAY}' not found on app stores yet.\n\n"
                    "Set `GOOGLE_PLAY_APP_ID` and/or `APP_STORE_APP_ID` in `.env` when available.")
    elif r:
        st.error(f"Error fetching app store data: {r.get('error')}")
    else:
        st.info("App Stores source is disabled. Enable it in the sidebar.")

# --- Footer ---
st.divider()
st.caption("Data is cached to reduce API calls. Use the Refresh button to fetch fresh data.")
