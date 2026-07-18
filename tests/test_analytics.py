"""Tests for summary-table helpers."""

import pandas as pd

from smart_energy_analytics.analytics import hourly_summary, room_summary


def example_data() -> pd.DataFrame:
    """Return two rows with different rooms and hours."""
    return pd.DataFrame(
        {
            "timestamp": ["2026-06-15 00:00:00", "2026-06-15 06:00:00"],
            "home_id": ["H-001", "H-001"],
            "room": ["Kitchen", "Living Room"],
            "appliance": ["Refrigerator", "Split AC"],
            "ac_usage_minutes": [10, 60],
            "occupancy_count": [0, 2],
            "temperature_band": ["Hot (34-38C)", "Very Hot (39-43C)"],
            "hourly_consumption_kwh": [0.8, 3.2],
        }
    )


def test_room_summary_totals_energy_by_room() -> None:
    """Each room receives its own consumption total."""
    summary = room_summary(example_data())

    assert summary["total_consumption_kwh"].sum() == 4.0
    assert set(summary["room"]) == {"Kitchen", "Living Room"}


def test_hourly_summary_uses_hour_of_day() -> None:
    """Hourly summaries group records by the derived hour column."""
    summary = hourly_summary(example_data())

    assert summary["hour"].tolist() == [0, 6]
