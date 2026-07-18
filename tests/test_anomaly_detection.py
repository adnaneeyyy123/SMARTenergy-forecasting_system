"""Tests for the IQR anomaly detector."""

import pandas as pd

from smart_energy_analytics.anomaly_detection import detect_consumption_anomalies


def test_detector_flags_a_large_consumption_value() -> None:
    """A value far beyond typical consumption should be marked as anomalous."""
    data = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-06-15", periods=4, freq="h"),
            "home_id": ["H-001"] * 4,
            "room": ["Living Room"] * 4,
            "appliance": ["Split AC"] * 4,
            "ac_usage_minutes": [20, 20, 20, 60],
            "occupancy_count": [1, 1, 1, 3],
            "temperature_band": ["Hot (34-38C)"] * 4,
            "hourly_consumption_kwh": [1.0, 1.1, 1.2, 20.0],
        }
    )

    result = detect_consumption_anomalies(data)

    assert result["is_anomaly"].tolist() == [False, False, False, True]
