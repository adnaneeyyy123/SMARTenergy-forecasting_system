"""Simple summary tables for residential-energy analysis."""

import pandas as pd

from .preprocessing import preprocess_energy_data


def room_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Return consumption, AC-use, and occupancy summaries for each room."""
    return _summarise(data, "room")


def appliance_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Return consumption, AC-use, and occupancy summaries for each appliance."""
    return _summarise(data, "appliance")


def daily_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Return one energy summary row for every calendar day across all homes."""
    return _summarise(data, "date")


def hourly_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Return one energy summary row for each hour of day, from 0 through 23."""
    return _summarise(data, "hour")


def _summarise(data: pd.DataFrame, group_column: str) -> pd.DataFrame:
    """Build a consistently shaped summary table for one grouping column."""
    prepared = preprocess_energy_data(data)
    summary = (
        prepared.groupby(group_column, as_index=False, dropna=False)
        .agg(
            record_count=("hourly_consumption_kwh", "size"),
            total_consumption_kwh=("hourly_consumption_kwh", "sum"),
            average_consumption_kwh=("hourly_consumption_kwh", "mean"),
            average_ac_usage_minutes=("ac_usage_minutes", "mean"),
            average_occupancy_count=("occupancy_count", "mean"),
        )
        .sort_values(group_column)
        .reset_index(drop=True)
    )
    numeric_columns = summary.select_dtypes(include="number").columns
    summary[numeric_columns] = summary[numeric_columns].round(2)
    return summary
