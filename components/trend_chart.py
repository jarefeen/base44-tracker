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
