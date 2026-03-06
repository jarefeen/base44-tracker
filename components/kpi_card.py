import streamlit as st


def render_kpi_card(label: str, value, delta=None, help_text: str | None = None):
    """Render a KPI metric card using st.metric."""
    st.metric(
        label=label,
        value=value if value is not None else "N/A",
        delta=delta,
        help=help_text,
    )
