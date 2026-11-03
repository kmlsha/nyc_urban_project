import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

TABLE_NAME = os.getenv("SR_TABLE", "service_requests")  # default to "service_requests" if not set
# load_dotenv() # load environment variables from .env file


# ----------------------------------------------------------------------------
# 1. Connection
# ----------------------------------------------------------------------------
def get_database_url():
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    try:
        return st.secrets["DATABASE_URL"]
    except Exception:
        return None


@st.cache_resource  # create the engine once, reuse it on every rerun
def get_engine(url):
    return create_engine(url, pool_pre_ping=True)


# ----------------------------------------------------------------------------
# 2. Load + clean
# ----------------------------------------------------------------------------
@st.cache_data(ttl=600, show_spinner="Loading data from MySQL...")  # remember for 10 minutes
def load_data():
    """Read the table once and return a clean DataFrame.

    Columns: id, created, closed, agency, category, borough, status,
             month, wd (weekday 0=Mon), hr (hour), dur_h (hours to close)
    """
    # Step 1: read only the columns we need
    sql = f"""
        SELECT unique_key, created_date, closed_date,
               agency, complaint_type, borough, status
        FROM {TABLE_NAME}
    """
    engine = get_engine(get_database_url())
    with engine.connect() as connection:
        df = pd.read_sql(text(sql), connection)

    # Step 2: friendlier column names
    df = df.rename(columns={
        "unique_key": "id",
        "created_date": "created",
        "closed_date": "closed",
        "complaint_type": "category",
    })

    # Step 3: make sure the dates are real dates
    df["created"] = pd.to_datetime(df["created"])
    df["closed"] = pd.to_datetime(df["closed"])

    # Step 4: columns calculated from the created date
    df["month"] = df["created"].dt.strftime("%Y-%m")   # '2024-03'
    df["wd"] = df["created"].dt.dayofweek               # 0 = Monday ... 6 = Sunday
    df["hr"] = df["created"].dt.hour                    # 0-23

    # Step 5: hours between created and closed
    #   empty if the request is still open, or if closed is before created
    hours = (df["closed"] - df["created"]).dt.total_seconds() / 3600
    df["dur_h"] = hours.where(hours >= 0)

    return df