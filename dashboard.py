"""Interactive Streamlit dashboard for Dubai residential-energy analytics.

Run with: ``streamlit run dashboard.py``
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from smart_energy_analytics.analytics import appliance_summary, hourly_summary, room_summary
from smart_energy_analytics.anomaly_detection import detect_consumption_anomalies
from smart_energy_analytics.forecasting import forecast_hourly_consumption
from smart_energy_analytics.preprocessing import load_energy_data


PROJECT_DIRECTORY = Path(__file__).resolve().parent
DATA_PATH = PROJECT_DIRECTORY / "data" / "raw" / "dubai_home_energy_hourly.csv"


@st.cache_data
def load_dashboard_data() -> pd.DataFrame:
    """Load and cache the project's source data for a responsive dashboard."""
    return load_energy_data(DATA_PATH)


def filter_data(data: pd.DataFrame) -> pd.DataFrame:
    """Render sidebar filters and return the selected records."""
    st.sidebar.header("Filter energy data")
    selected_homes = st.sidebar.multiselect("Home", sorted(data["home_id"].unique()))
    selected_rooms = st.sidebar.multiselect("Room", sorted(data["room"].unique()))
    selected_appliances = st.sidebar.multiselect("Appliance", sorted(data["appliance"].unique()))
    selected_bands = st.sidebar.multiselect(
        "Temperature band", sorted(data["temperature_band"].unique())
    )
    start_date, end_date = st.sidebar.date_input(
        "Date range",
        value=(data["date"].min().date(), data["date"].max().date()),
        min_value=data["date"].min().date(),
        max_value=data["date"].max().date(),
    )

    filtered = data.loc[data["date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date))]
    for column, selections in (
        ("home_id", selected_homes),
        ("room", selected_rooms),
        ("appliance", selected_appliances),
        ("temperature_band", selected_bands),
    ):
        if selections:
            filtered = filtered.loc[filtered[column].isin(selections)]
    return filtered.copy()


def show_kpis(data: pd.DataFrame, anomalies: pd.DataFrame) -> None:
    """Display the four headline metrics for the current filter selection."""
    total = data["hourly_consumption_kwh"].sum()
    average = data["hourly_consumption_kwh"].mean()
    peak = data["hourly_consumption_kwh"].max()
    flagged_count = int(anomalies["is_anomaly"].sum())

    total_card, average_card, peak_card, anomaly_card = st.columns(4)
    total_card.metric("Total consumption", f"{total:.2f} kWh")
    average_card.metric("Average per record", f"{average:.2f} kWh")
    peak_card.metric("Peak record", f"{peak:.2f} kWh")
    anomaly_card.metric("Anomaly alerts", flagged_count)


def show_charts(data: pd.DataFrame) -> None:
    """Render time, room, appliance, and hourly consumption charts."""
    timeline = (
        data.groupby("timestamp", as_index=False)["hourly_consumption_kwh"].sum().sort_values("timestamp")
    )
    rooms = room_summary(data).sort_values("total_consumption_kwh")
    appliances = appliance_summary(data).sort_values("total_consumption_kwh", ascending=False)
    hours = hourly_summary(data)

    st.subheader("Consumption pattern")
    time_chart = px.line(
        timeline,
        x="timestamp",
        y="hourly_consumption_kwh",
        markers=True,
        labels={"hourly_consumption_kwh": "Combined consumption (kWh)", "timestamp": "Time"},
    )
    time_chart.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=320)
    st.plotly_chart(time_chart, use_container_width=True)

    room_column, appliance_column = st.columns(2)
    with room_column:
        room_chart = px.bar(
            rooms,
            x="total_consumption_kwh",
            y="room",
            orientation="h",
            labels={"total_consumption_kwh": "Total kWh", "room": "Room"},
        )
        room_chart.update_layout(title="Room-wise consumption", margin=dict(l=0, r=0, t=45, b=0))
        st.plotly_chart(room_chart, use_container_width=True)
    with appliance_column:
        appliance_chart = px.bar(
            appliances.head(8),
            x="appliance",
            y="total_consumption_kwh",
            labels={"total_consumption_kwh": "Total kWh", "appliance": "Appliance"},
        )
        appliance_chart.update_layout(title="Top appliances", margin=dict(l=0, r=0, t=45, b=0))
        st.plotly_chart(appliance_chart, use_container_width=True)

    hourly_chart = px.bar(
        hours,
        x="hour",
        y="total_consumption_kwh",
        labels={"hour": "Hour of day", "total_consumption_kwh": "Total kWh"},
    )
    hourly_chart.update_layout(title="Hourly consumption profile", margin=dict(l=0, r=0, t=45, b=0))
    st.plotly_chart(hourly_chart, use_container_width=True)


def show_anomalies(anomalies: pd.DataFrame) -> None:
    """Show a clear alert and a compact table when unusual readings exist."""
    flagged = anomalies.loc[anomalies["is_anomaly"]].copy()
    st.subheader("Anomaly alerts")
    if flagged.empty:
        st.success("No unusual consumption records were detected in the current selection.")
        return

    st.warning(f"{len(flagged)} record(s) fall outside the typical consumption range.")
    columns = ["timestamp", "home_id", "room", "appliance", "hourly_consumption_kwh", "temperature_band"]
    st.dataframe(flagged[columns].sort_values("hourly_consumption_kwh", ascending=False), hide_index=True)


def show_forecast(data: pd.DataFrame) -> None:
    """Present the next four combined-consumption predictions when possible."""
    st.subheader("Short-term forecast")
    try:
        forecast = forecast_hourly_consumption(data, periods=4)
    except ValueError as error:
        st.info(f"Forecast unavailable for this selection: {error}")
        return

    st.caption("A straight-line trend based on combined historical consumption.")
    st.dataframe(forecast, hide_index=True)


def show_insights(data: pd.DataFrame) -> None:
    """Write concise, data-driven observations in Dubai residential context."""
    top_appliance = (
        data.groupby("appliance")["hourly_consumption_kwh"].sum().sort_values(ascending=False).index[0]
    )
    top_room = data.groupby("room")["hourly_consumption_kwh"].sum().sort_values(ascending=False).index[0]
    ac_share = (
        data.loc[data["appliance"].eq("Split AC"), "hourly_consumption_kwh"].sum()
        / data["hourly_consumption_kwh"].sum()
        * 100
    )
    peak = data.loc[data["hourly_consumption_kwh"].idxmax()]

    st.subheader("Dubai home insights")
    st.markdown(
        f"- **Cooling demand dominates:** Split AC accounts for **{ac_share:.0f}%** of selected consumption. "
        "This is consistent with the high cooling load expected during Dubai's hotter periods.\n"
        f"- **Priority area:** **{top_room}** has the highest room-level consumption, while "
        f"**{top_appliance}** is the leading appliance.\n"
        f"- **Peak-use context:** the highest single record is **{peak['hourly_consumption_kwh']:.2f} kWh** "
        f"at {peak['timestamp']:%d %b, %H:%M} in the {peak['room']}."
    )


def main() -> None:
    """Configure and render the complete dashboard."""
    st.set_page_config(page_title="Dubai Home Energy Analytics", page_icon="⚡", layout="wide")
    st.title("Smart Residential Energy Analytics")
    st.caption("Explore residential energy use, cooling demand, anomalies, and near-term consumption in Dubai homes.")

    data = filter_data(load_dashboard_data())
    if data.empty:
        st.info("No records match the selected filters. Adjust the filters to continue.")
        return

    anomalies = detect_consumption_anomalies(data)
    show_kpis(data, anomalies)
    st.divider()
    show_charts(data)
    show_anomalies(anomalies)
    show_forecast(data)
    show_insights(data)


if __name__ == "__main__":
    main()
