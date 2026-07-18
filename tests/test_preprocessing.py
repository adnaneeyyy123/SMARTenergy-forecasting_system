"""Tests for data-preparation helpers."""

import pandas as pd
import pytest

from smart_energy_analytics.preprocessing import preprocess_energy_data, validate_energy_data


def sample_data() -> pd.DataFrame:
    """Return one valid example record for focused tests."""
    return pd.DataFrame(
        {
            "timestamp": ["2026-06-15 12:00:00"],
            "home_id": ["H-001"],
            "room": ["Living Room"],
            "appliance": ["Split AC"],
            "ac_usage_minutes": [60],
            "occupancy_count": [2],
            "temperature_band": ["Extreme Heat (44C+)"],
            "hourly_consumption_kwh": [3.86],
        }
    )


def test_preprocessing_adds_date_and_hour() -> None:
    """Preprocessing derives date and hour columns from timestamps."""
    prepared = preprocess_energy_data(sample_data())

    assert prepared.loc[0, "hour"] == 12
    assert prepared.loc[0, "date"] == pd.Timestamp("2026-06-15")


def test_preprocessing_rejects_invalid_ac_usage() -> None:
    """AC use cannot exceed the number of minutes in an hour."""
    data = sample_data()
    data.loc[0, "ac_usage_minutes"] = 61

    with pytest.raises(ValueError, match="ac_usage_minutes"):
        preprocess_energy_data(data)


def test_validation_rejects_an_invalid_timestamp() -> None:
    """Validation also protects callers that do not preprocess first."""
    data = sample_data()
    data.loc[0, "timestamp"] = "not-a-date"

    with pytest.raises(ValueError, match="timestamp"):
        validate_energy_data(data)
