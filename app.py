"""
Urban Pulse - NYC 311 complaint analytics

Project layout:
    app.py                 sidebar + page routing (this file)
    demand_pages.py        what / where / when pages
    resolution_pages.py    resolution time and closure pages
    utils.py               shared helpers
    database/db.py         MySQL connection + clean request table
    database/queries.py    reusable query functions

Run:
    streamlit run app.py
"""

import streamlit as st

import demand_pages as demand
import resolution_pages as resolution
from database.db import get_database_url
from database.queries import clear_cache

st.set_page_config(page_title="Urban Pulse", page_icon="🏙️", layout="wide")

if not get_database_url():
    st.error("DATABASE_URL is not set. Add it as an environment variable or in .streamlit/secrets.toml.")
    st.stop()

# ---------------- Created Sidebar(s) with respect to tasks provided ----------------
PAGES = [
    "Overview", # KPI page
    "1. Complaint categories",
    "2. Agency workload",
    "3. Borough analysis",
    "4. Monthly trend",
    "5. Weekday/hour demand",
    "6. Status analysis",
    "7. Resolution statistics",
    "8. Resolution by category",
    "9. Resolution by agency",
    "10. Outlier investigation",
    "11. Skewness & distribution",
    "12. Closure-rate comparison",
    "13. Volume vs duration",
    "14. High-volume & long-duration",
]
page = st.sidebar.radio("Pages", PAGES)

with st.sidebar.expander("Settings"):
    top_n = st.slider("Top N", 5, 25, 10)
    min_n = st.number_input("Min requests per group", 1, 10000, 30)
    if st.button("Refresh data"):
        clear_cache()
        st.rerun()

st.title("🏙️ Urban Pulse")
st.title("NYC 311 Citizen Complaint Intelligence & Resolution Analytics")
st.subheader(page)

# ---------------- Routing using if-elif statements ----------------
if page == "Overview":
    demand.overview()
elif page == "1. Complaint categories":
    demand.complaint_categories(top_n)
elif page == "2. Agency workload":
    demand.agency_workload()
elif page == "3. Borough analysis":
    demand.borough_analysis()
elif page == "4. Monthly trend":
    demand.monthly_trend()
elif page == "5. Weekday/hour demand":
    demand.weekday_hour_demand()
elif page == "6. Status analysis":
    demand.status_analysis()
elif page == "7. Resolution statistics":
    resolution.resolution_statistics()
elif page == "8. Resolution by category":
    resolution.resolution_by_category(top_n, min_n)
elif page == "9. Resolution by agency":
    resolution.resolution_by_agency(min_n)
elif page == "10. Outlier investigation":
    resolution.outlier_investigation(top_n, min_n)
elif page == "11. Skewness & distribution":
    resolution.skewness_distribution()
elif page == "12. Closure-rate comparison":
    resolution.closure_rate_comparison(min_n)
elif page == "13. Volume vs duration":
    resolution.volume_vs_duration(min_n)
elif page == "14. High-volume & long-duration":
    resolution.high_volume_long_duration(min_n)