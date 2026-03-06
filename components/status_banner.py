import streamlit as st


def render_status_banner(sources: list[dict]):
    """Show green/red status dots for each data source.

    sources: list of {"name": str, "available": bool, "ok": bool}
    """
    cols = st.columns(len(sources))
    for col, src in zip(cols, sources):
        if not src["available"]:
            icon, status = "⚪", "Not configured"
        elif src["ok"]:
            icon, status = "🟢", "OK"
        else:
            icon, status = "🔴", "Error"
        col.markdown(f"{icon} **{src['name']}**: {status}")
