import plotly.express as px
import streamlit as st

px.defaults.template = "plotly_dark"

SLOW_HOURS = 48  # requests taking longer than this count as "slow"
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def show(fig):
    """Display a plotly chart at full width."""
    st.plotly_chart(fig, use_container_width=True)


def add_share(df, column="requests"):
    """Add a share_% column (each row's percentage of the total)."""
    df["share_in_perc"] = (df[column] / df[column].sum() * 100).round(2)
    return df
