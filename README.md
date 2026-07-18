# Smart Residential Energy Analytics for Dubai Homes

An educational Python project for exploring synthetic, room-level electricity
use in Dubai residences. It turns hourly readings into clear summaries,
unusual-use alerts, a short-term forecast, and an interactive dashboard.

> The included data is synthetic. Use the project for learning and prototyping,
> not billing, operational decisions, or analysis of real household identities.

## Features

- Validates and prepares energy readings with `date` and `hour` fields.
- Summarises consumption by room, appliance, day, and hour.
- Flags unusually high or low records using an explainable IQR rule.
- Forecasts the next few observed intervals with a simple linear trend.
- Provides a Streamlit dashboard with filters, KPIs, charts, alerts, and Dubai-focused insights.

## Project layout

```text
smart-residential-energy-analytics/
├── data/raw/                         # Synthetic source data
├── data/processed/                   # Generated outputs (not tracked)
├── docs/                             # Summary and presentation outline
├── src/smart_energy_analytics/       # Reusable analysis modules
├── tests/                            # Automated tests
├── dashboard.py                      # Streamlit entry point
├── pyproject.toml                    # Package and runtime configuration
└── requirements.txt                  # Local development installation
```

## Setup

Python **3.10 or later** is required. If you previously created this project
with Python 3.9, delete and recreate `.venv` before continuing.

```bash
cd smart-residential-energy-analytics
python3.10 -m venv .venv
source .venv/bin/activate            # macOS/Linux
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Run the dashboard

```bash
streamlit run dashboard.py
```

Use the sidebar to filter by home, room, appliance, temperature band, or date.
The dashboard refreshes its KPI cards, charts, anomaly alerts, forecast, and
Dubai residential-energy insights for the selected records.

## Use the modules in Python

```python
from smart_energy_analytics.analytics import room_summary
from smart_energy_analytics.anomaly_detection import detect_consumption_anomalies
from smart_energy_analytics.forecasting import forecast_hourly_consumption
from smart_energy_analytics.preprocessing import load_energy_data

data = load_energy_data("data/raw/dubai_home_energy_hourly.csv")
print(room_summary(data))
print(detect_consumption_anomalies(data).query("is_anomaly"))
print(forecast_hourly_consumption(data, periods=4))
```

## Methods and limitations

The anomaly detector uses the interquartile range (IQR), flagging values beyond
the typical middle range. A high reading may still be valid during Dubai's
extreme heat, so always review its room, appliance, occupancy, and temperature
context.

The forecast combines consumption at each timestamp and extends its straight-line
trend. It is a clear short-term baseline, but it does not model weather,
weekends, daily routines, occupancy changes, or unexpected appliance use.

## Testing

Run all automated tests after setup:

```bash
python -m pytest
```

See `docs/project_summary.md` for a concise project overview and
`docs/presentation_outline.md` for a ready-to-use presentation structure.
