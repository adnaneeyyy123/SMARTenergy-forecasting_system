"""A transparent rule-based detector for unusually high or low consumption."""

import pandas as pd

from .preprocessing import preprocess_energy_data


def detect_consumption_anomalies(
    data: pd.DataFrame,
    iqr_multiplier: float = 1.5,
) -> pd.DataFrame:
    """Mark records whose consumption falls outside the interquartile range.

    The interquartile range (IQR) is the distance between the 25th and 75th
    percentiles. Values below ``Q1 - multiplier * IQR`` or above
    ``Q3 + multiplier * IQR`` are marked as anomalies. The default multiplier
    of 1.5 is a common, easy-to-explain exploratory-analysis rule.

    Args:
        data: Raw or preprocessed hourly energy records.
        iqr_multiplier: How far from the typical range a value must be before
            it is flagged. Larger values produce fewer flags.

    Returns:
        A copy of the data with lower/upper bounds and an ``is_anomaly`` flag.

    Raises:
        ValueError: If ``iqr_multiplier`` is not positive.
    """
    if iqr_multiplier <= 0:
        raise ValueError("iqr_multiplier must be greater than zero")

    detected = preprocess_energy_data(data)
    consumption = detected["hourly_consumption_kwh"]
    first_quartile = consumption.quantile(0.25)
    third_quartile = consumption.quantile(0.75)
    interquartile_range = third_quartile - first_quartile

    lower_bound = first_quartile - iqr_multiplier * interquartile_range
    upper_bound = third_quartile + iqr_multiplier * interquartile_range
    detected["anomaly_lower_bound_kwh"] = round(lower_bound, 2)
    detected["anomaly_upper_bound_kwh"] = round(upper_bound, 2)
    detected["is_anomaly"] = (consumption < lower_bound) | (consumption > upper_bound)
    return detected
