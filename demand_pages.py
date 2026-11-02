# task list fn from 1 to 6

import plotly.express as px
import streamlit as st


from database.db import load_data
from database.queries import count_by, get_durations, total_requests
from utils import SLOW_HOURS, WEEKDAYS, add_share, show


def overview(top_n):
    df = load_data()
    total = len(df)
    closed = df["closed"].notna().sum()          # requests with a closed date
    hours = get_durations()["dur_h"]
    st.header("5 KPIs generated using the NYC dataset")
    cols = st.columns(5) # 5 KPI added here
    cols[0].metric("Total requests", f"{total:,}") #1st  - Total requests
    cols[1].metric("Recorded closure", f"{closed / total * 100:.1f}%") #2nd - Record/closed perc
    cols[2].metric("Open requests", f"{total - closed:,}") #3rd - Open req
    cols[3].metric("Median resolution", f"{hours.median():.1f} hrs") #4th - Median resolution
    cols[4].metric(f"Over {SLOW_HOURS} hours", f"{(hours > SLOW_HOURS).mean() * 100:.1f}%") #5th - Over dyn hrs

def complaint_categories(top_n):
    cat = count_by("category", top_n)
    cat["share in percentage"] = (cat["requests"] / total_requests() * 100).round(2)  # share of ALL requests
    show(px.bar(cat.sort_values("requests"), x="requests", y="category", orientation="h"))
    st.dataframe(cat)


def agency_workload():
    print("agency  -- ",add_share(count_by("agency")))
    agency = add_share(count_by("agency"))
    show(px.bar(agency.head(15).sort_values("requests",ascending=False), x="agency", y="requests"))
    st.dataframe(agency)


def borough_analysis():
    borough = add_share(count_by("borough"))
    show(px.bar(borough, x="borough", y="requests", text="share_in_perc"))


def monthly_trend():
    df = load_data()
    daily = df.groupby(df["created"].dt.date).size().reset_index(name="requests")
    daily.columns = ["date", "requests"]
    daily["change_vs_prev_day_%"] = (daily["requests"].pct_change() * 100).round(2)
    show(px.line(daily, x="date", y="requests", markers=True))


def weekday_hour_demand():
    df = load_data()
    # Rows = weekday (0-6), columns = hour (0-23), values = number of requests
    grid = df.groupby(["wd", "hr"]).size().unstack(fill_value=0)
    grid = grid.reindex(index=range(7), columns=range(24), fill_value=0)
    grid.index = WEEKDAYS

    by_day = grid.sum(axis=1).rename_axis("weekday").reset_index(name="requests")
    by_hour = grid.sum(axis=0).rename_axis("hour").reset_index(name="requests")
    st.plotly_chart(px.bar(by_day, x="weekday", y="requests",text="requests"), use_container_width=True)
    st.plotly_chart(px.bar(by_hour, x="hour", y="requests"), use_container_width=True)



def status_analysis():
    status = add_share(count_by("status"))
    left, right = st.columns(2)
    right.plotly_chart(px.bar(status, x="status", y="requests"), use_container_width=True)
    left.plotly_chart(px.pie(status, names="status", values="requests", hole=0.45), use_container_width=True)
