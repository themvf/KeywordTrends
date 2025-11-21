from typing import Any, Dict, List

import pandas as pd
import plotly.express as px
import streamlit as st


def stat_cards(summary: Dict[str, Any]) -> None:
    cols = st.columns(len(summary))
    for col, (label, value) in zip(cols, summary.items()):
        col.metric(label, value)


def render_table(title: str, rows: List[Dict[str, Any]]) -> None:
    st.subheader(title)
    if not rows:
        st.info("No data yet.")
        return
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)


def price_histogram(rows: List[Dict[str, Any]]) -> None:
    prices = [r.get("price") for r in rows if r.get("price") is not None]
    if not prices:
        st.info("No prices available.")
        return
    fig = px.histogram(prices, nbins=15, labels={"value": "Price"})
    st.plotly_chart(fig, use_container_width=True)


def keyword_bar(df: pd.DataFrame, column: str = "platform") -> None:
    if df.empty:
        st.info("No keyword data available.")
        return
    melted = df.melt(id_vars=["term"], value_vars=[c for c in df.columns if c != "term"])
    fig = px.bar(melted, x="term", y="value", color="variable", labels={"value": "count"})
    st.plotly_chart(fig, use_container_width=True)
