"""A beginner-friendly short-term consumption forecasting baseline."""

import pandas as pd

from .preprocessing import preprocess_energy_data


def forecast_hourly_consumption(data: pd.DataFrame, periods: int = 4) -> pd.DataFrame:
    """Forecast combined consumption for the next few observed time intervals.

    Records sharing a timestamp are first added together. A straight line is
    then fitted to those totals: each new interval continues the average trend
    seen in the historical series. The output is clipped at zero because energy
    consumption cannot be negative.

    Args:
        data: Raw or preprocessed hourly energy records.
        periods: Number of future time intervals to forecast. The interval is
            inferred from the median gap between timestamps.

    Returns:
        A dataframe with future ``timestamp`` and
        ``forecast_consumption_kwh`` columns.

    Raises:
        ValueError: If fewer than two distinct timestamps are available or
            ``periods`` is not a positive integer.
    """
    if not isinstance(periods, int) or isinstance(periods, bool) or periods < 1:
        raise ValueError("periods must be a positive integer")

    prepared = preprocess_energy_data(data)
    historical = (
        prepared.groupby("timestamp", as_index=True)["hourly_consumption_kwh"]
        .sum()
        .sort_index()
    )
    if len(historical) < 2:
        raise ValueError("At least two distinct timestamps are required to forecast")

    # The median interval keeps one irregular timestamp from changing the forecast cadence.
    interval = historical.index.to_series().diff().dropna().median()
    if interval <= pd.Timedelta(0):
        raise ValueError("Timestamps must increase over time")

    time_steps = pd.Series(range(len(historical)), dtype="float64")
    consumption = historical.reset_index(drop=True).astype("float64")
    slope = _linear_slope(time_steps, consumption)
    intercept = consumption.mean() - slope * time_steps.mean()

    future_steps = pd.Series(range(len(historical), len(historical) + periods))
    forecasts = (intercept + slope * future_steps).clip(lower=0).round(2)
    future_timestamps = [historical.index[-1] + interval * step for step in range(1, periods + 1)]
    return pd.DataFrame(
        {
            "timestamp": future_timestamps,
            "forecast_consumption_kwh": forecasts,
        }
    )


def _linear_slope(time_steps: pd.Series, consumption: pd.Series) -> float:
    """Calculate a least-squares slope without introducing a model dependency."""
    centered_time = time_steps - time_steps.mean()
    denominator = (centered_time**2).sum()
    if denominator == 0:
        return 0.0
    return float((centered_time * (consumption - consumption.mean())).sum() / denominator)
