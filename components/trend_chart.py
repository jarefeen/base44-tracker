import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd


CHART_TEMPLATE = "plotly_dark"
BRAND_COLOR = "#4F46E5"


def render_line_chart(df: pd.DataFrame, x: str, y: str, title: str = ""):
    if df.empty:
        st.info("No data available for chart.")
        return

    fig = px.line(df, x=x, y=y, title=title, template=CHART_TEMPLATE)
    fig.update_traces(line_color=BRAND_COLOR, line_width=2.5)
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=350,
        xaxis_title="",
        yaxis_title="",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_multi_line_chart(df: pd.DataFrame, x: str, y_columns: list[str], title: str = "", highlight: str | None = None):
    """Render multiple lines on the same chart. Highlight one line if specified."""
    if df.empty:
        st.info("No data available for chart.")
        return

    fig = go.Figure()
    colors = ["#4F46E5", "#EF4444", "#F59E0B", "#10B981", "#8B5CF6"]
    for i, col in enumerate(y_columns):
        is_highlighted = (col == highlight)
        fig.add_trace(go.Scatter(
            x=df[x], y=df[col], name=col,
            line=dict(
                color=colors[i % len(colors)],
                width=3.5 if is_highlighted else 1.5,
            ),
            opacity=1.0 if is_highlighted else 0.6,
        ))
    fig.update_layout(
        title=title,
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=40, b=20),
        height=400,
        xaxis_title="",
        yaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_bar_chart(df: pd.DataFrame, x: str, y: str, title: str = "", horizontal: bool = False):
    if df.empty:
        st.info("No data available for chart.")
        return

    if horizontal:
        fig = px.bar(df, x=y, y=x, orientation="h", title=title, template=CHART_TEMPLATE)
    else:
        fig = px.bar(df, x=x, y=y, title=title, template=CHART_TEMPLATE)
    fig.update_traces(marker_color=BRAND_COLOR)
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=350,
        xaxis_title="",
        yaxis_title="",
    )
    st.plotly_chart(fig, use_container_width=True)
