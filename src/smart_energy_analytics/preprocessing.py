"""Functions for loading, checking, and preparing energy-consumption data."""

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = frozenset(
    {
        "timestamp",
        "home_id",
        "room",
        "appliance",
        "ac_usage_minutes",
        "occupancy_count",
        "temperature_band",
        "hourly_consumption_kwh",
    }
)

NUMERIC_COLUMNS = ("ac_usage_minutes", "occupancy_count", "hourly_consumption_kwh")
TEXT_COLUMNS = ("home_id", "room", "appliance", "temperature_band")


def load_energy_data(file_path: str | Path) -> pd.DataFrame:
    """Load a CSV file and return cleaned, analysis-ready hourly energy records.

    The source timestamps are interpreted as Gulf Standard Time (Asia/Dubai),
    but remain timezone-naive so they work easily in beginner pandas workflows.
    """
    data = pd.read_csv(file_path)
    return preprocess_energy_data(data)


def preprocess_energy_data(data: pd.DataFrame) -> pd.DataFrame:
    """Validate and standardise energy data without changing the input dataframe.

    The returned dataframe has parsed ``timestamp`` values plus ``date`` and
    ``hour`` columns, which are convenient for daily and hourly analysis.

    Raises:
        ValueError: If required data is missing or contains invalid values.
    """
    cleaned = data.copy()
    _check_required_columns(cleaned)

    cleaned["timestamp"] = pd.to_datetime(cleaned["timestamp"], errors="raise")
    for column in NUMERIC_COLUMNS:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="raise")
    for column in TEXT_COLUMNS:
        cleaned[column] = cleaned[column].astype("string").str.strip()

    validate_energy_data(cleaned)
    cleaned["date"] = cleaned["timestamp"].dt.normalize()
    cleaned["hour"] = cleaned["timestamp"].dt.hour
    return cleaned


def validate_energy_data(data: pd.DataFrame) -> None:
    """Raise ``ValueError`` when data violates the project's quality rules.

    This function is useful before saving data received from another source.
    It checks required columns, missing values, non-negative consumption and
    occupancy, and AC usage between zero and 60 minutes per hourly record.
    """
    _check_required_columns(data)
    required_data = data[list(REQUIRED_COLUMNS)]
    if required_data.isna().any().any():
        missing = required_data.columns[required_data.isna().any()].tolist()
        raise ValueError(f"Required columns contain missing values: {missing}")

    parsed_timestamps = pd.to_datetime(data["timestamp"], errors="coerce")
    if parsed_timestamps.isna().any():
        raise ValueError("timestamp contains invalid or missing values")

    for column in TEXT_COLUMNS:
        if data[column].astype("string").str.strip().eq("").any():
            raise ValueError(f"{column} cannot contain blank values")

    _check_numeric_column(data, "hourly_consumption_kwh", minimum=0)
    _check_numeric_column(data, "occupancy_count", minimum=0)
    _check_numeric_column(data, "ac_usage_minutes", minimum=0, maximum=60)


def _check_required_columns(data: pd.DataFrame) -> None:
    """Raise a helpful error if one or more required columns are absent."""
    missing = sorted(REQUIRED_COLUMNS.difference(data.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _check_numeric_column(
    data: pd.DataFrame,
    column: str,
    minimum: float,
    maximum: float | None = None,
) -> None:
    """Check numeric bounds for one data column."""
    values = pd.to_numeric(data[column], errors="coerce")
    if values.isna().any():
        raise ValueError(f"{column} must contain numeric values")
    if (values < minimum).any():
        raise ValueError(f"{column} cannot be less than {minimum}")
    if maximum is not None and (values > maximum).any():
        raise ValueError(f"{column} cannot be greater than {maximum}")
