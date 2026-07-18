"""Tools for preparing and summarising Dubai residential-energy data."""

from .analytics import (
    appliance_summary,
    daily_summary,
    hourly_summary,
    room_summary,
)
from .anomaly_detection import detect_consumption_anomalies
from .forecasting import forecast_hourly_consumption
from .preprocessing import load_energy_data, preprocess_energy_data, validate_energy_data

__all__ = [
    "appliance_summary",
    "daily_summary",
    "detect_consumption_anomalies",
    "forecast_hourly_consumption",
    "hourly_summary",
    "load_energy_data",
    "preprocess_energy_data",
    "room_summary",
    "validate_energy_data",
]
