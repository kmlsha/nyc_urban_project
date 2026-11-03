# task list fn from 7 to 14
import numpy as np
import plotly.express as px
import streamlit as st

from database.queries import closure_by, count_by, get_durations, median_by, total_requests
from utils import show


def resolution_statistics():
    hours = get_durations()["dur_h"]
    st.subheader("Resolution time statistics provided by hours")
    st.caption(
        f"{len(hours):,} of {total_requests():,} requests are included. "
        "Requests with missing or negative resolution times are excluded.")
    stats = hours.describe(percentiles=[0.25, 0.5, 0.75]).to_frame("hours")
    stats["days"] = stats["hours"] / 24
    stats.loc["count", "days"] = np.nan
    st.dataframe(stats.round(2), use_container_width=True)


def resolution_by_category(top_n, min_n):
    result = median_by("category", min_n)
    show(px.bar(result.head(top_n).sort_values("median_hours"), x="median_hours", y="category",
                orientation="h", hover_data=["valid_requests"]))
    st.dataframe(result.round(2), use_container_width=True)


def resolution_by_agency(min_n):
    result = median_by("agency", min_n)
    show(px.bar(result.head(20).sort_values("median_hours"), x="median_hours", y="agency",
                orientation="h", hover_data=["valid_requests"]))


def outlier_investigation(top_n, min_n):
    # IQR rule: anything above Q3 + 1.5 * IQR is an unusually long resolution.
    data = get_durations()
    hours = data["dur_h"]
    q1, q3 = hours.quantile(0.25), hours.quantile(0.75)
    iqr = q3 - q1
    upper_fence = q3 + 1.5 * iqr
    data["outlier"] = hours > upper_fence

    cols = st.columns(4)
    cols[0].metric("Q1", f"{q1:,.2f}")
    cols[1].metric("Q3", f"{q3:,.2f}")
    cols[2].metric("IQR", f"{iqr:,.2f}")
    cols[3].metric("Outliers", f"{data['outlier'].sum():,} ({data['outlier'].mean() * 100:.1f}%)")

    top_categories = data["category"].value_counts().head(top_n).index
    show(px.box(data[data["category"].isin(top_categories)], x="category", y="dur_h", log_y=True, points=False))


def skewness_distribution():
    hours = get_durations()["dur_h"]
    print("skewness_distribution - hours -  ",hours)
    cols = st.columns(3)
    cols[0].metric("Skewness", f"{hours.skew():.2f}")
    cols[1].metric("Mean / median", f"{hours.mean() / max(hours.median(), 1e-9):.2f}x")
    cols[2].metric("Skewness (log)", f"{np.log1p(hours).skew():.2f}")

    fig = px.histogram(hours[hours <= hours.quantile(0.99)], nbins=80, labels={"value": "Hours"})
    fig.update_layout(showlegend=False)
    show(fig)


def closure_rate_comparison(min_n):
    st.subheader("Closure rate by agency, borough and category")
    st.caption("Closure rate = closed requests / total requests. "
               "Groups with fewer than the minimum number of requests are skipped.")
    for by in ["agency", "borough", "category"]:
        rates = closure_by(by)
        st.header(by.capitalize())
        rates = rates[rates["requests"] >= min_n].sort_values("closure_rate_%")
        show(px.bar(rates.head(25), y="closure_rate_%", x=by, hover_data=["requests", "closed"]))


def volume_vs_duration(min_n):
    merged = count_by("category").merge(median_by("category", min_n), on="category")
    rho = merged["requests"].rank().corr(merged["median_hours"].rank())
    st.metric("Spearman correlation (volume vs median hours)", f"{rho:.2f}")
    show(px.scatter(merged, x="requests", y="median_hours", hover_name="category", log_x=True, log_y=True))

def high_volume_long_duration(min_n):
    # Categories in the top 25% by volume AND the top 25% by median resolution time.
    merged = count_by("category").merge(median_by("category", min_n), on="category")
 
    vol_cut = merged["requests"].quantile(0.75)
    dur_cut = merged["median_hours"].quantile(0.75)
 
    hits = merged[(merged["requests"] >= vol_cut) & (merged["median_hours"] >= dur_cut)]
    hits = hits.sort_values("requests", ascending=False)
    hits = hits[["category", "requests", "median_hours"]].rename(columns={"category": "complaint_type"})
 
    st.caption(f"Example cut-offs: volume ≥ {vol_cut:,.0f} requests "
               f"and median duration ≥ {dur_cut:,.1f} hours.")
    st.dataframe(hits, use_container_width=True)