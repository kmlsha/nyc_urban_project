import streamlit as st

from database.db import load_data


# ----------------------------------------------------------------------------
# Counting requests
# ----------------------------------------------------------------------------
def total_requests():
    """How many distinct requests exist."""
    return len(load_data())


def count_by(column, limit=None):
    """Requests per value of `column`, biggest first.

    count_by("agency", 10)  ->  top 10 agencies
    """
    df = load_data()
    counts = df[column].value_counts().reset_index()
    counts.columns = [column, "requests"]
    return counts.head(limit) if limit else counts


# ----------------------------------------------------------------------------
# Closure rate
# ----------------------------------------------------------------------------
def closure_by(column):
    """Requests, closed requests and closure rate (%) per value of `column`."""
    df = load_data()
    result = df.groupby(column).agg(
        requests=("id", "count"),
        closed=("closed", "count"),   # count() only counts non-empty values
    ).reset_index()
    result["closure_rate_%"] = (result["closed"] / result["requests"] * 100).round(2)
    return result


# ----------------------------------------------------------------------------
# Resolution time
# ----------------------------------------------------------------------------
def get_durations():
    """One row per request that has a valid resolution time (dur_h)."""
    df = load_data()
    valid = df[df["dur_h"].notna()]
    print("valid --",valid )
    return valid[["category", "agency", "borough", "dur_h"]]


def median_by(column, min_requests):
    """Median resolution hours per value of `column`, slowest first.

    Groups with fewer than `min_requests` closed requests are skipped,
    because a median of 2 requests is not reliable.
    """
    durations = get_durations()

    stats = durations.groupby(column)["dur_h"].agg(
        valid_requests="count",
        median_hours="median",
        mean_hours="mean",
    )
    stats = stats[stats["valid_requests"] >= min_requests]

    return stats.reset_index().sort_values("median_hours", ascending=False)


# ----------------------------------------------------------------------------
# Cache
# ----------------------------------------------------------------------------
def clear_cache():
    """Forget the loaded data so the next page load re-reads MySQL."""
    st.cache_data.clear()