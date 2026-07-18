"""Tests for the linear-trend forecasting baseline."""

import pandas as pd

from smart_energy_analytics.forecasting import forecast_hourly_consumption


def test_forecast_extends_a_simple_upward_trend() -> None:
    """A one-kWh hourly increase should continue in the forecast."""
    data = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-06-15", periods=3, freq="h"),
            "home_id": ["H-001"] * 3,
            "room": ["Living Room"] * 3,
            "appliance": ["Split AC"] * 3,
            "ac_usage_minutes": [20, 30, 40],
            "occupancy_count": [1, 1, 1],
            "temperature_band": ["Hot (34-38C)"] * 3,
            "hourly_consumption_kwh": [1.0, 2.0, 3.0],
        }
    )

    result = forecast_hourly_consumption(data, periods=2)

    assert result["forecast_consumption_kwh"].tolist() == [4.0, 5.0]
    assert result["timestamp"].tolist() == [
        pd.Timestamp("2026-06-15 03:00:00"),
        pd.Timestamp("2026-06-15 04:00:00"),
    ]
