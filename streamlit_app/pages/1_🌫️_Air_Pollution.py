from datetime import datetime, timedelta, date
import pydeck as pdk

import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from smartcity.database import read_db_between_dates, read_db
from smartcity.config import TABLE_NAME_MEASUREMENTS, TABLE_NAME_LOCATIONS
from smartcity.utils import get_dates_range
from utils import POLLUTANTS_INFO, POLLUTANTS_LIMITS, add_sidebar_title

HIST_DAYS = 31  # 2 * 7 + 1


def show_sensor_map(sensors: pd.DataFrame):
    st.markdown("#### 🌍 Sensor Locations")
    st.caption(
        "Interactive map showing the location and characteristics of monitoring stations around Clermont-Ferrand."
    )
    grouped = (
        sensors.groupby(
            [
                "id",
                "name",
                "locality",
                "owner_name",
                "provider_name",
                "latitude",
                "longitude",
                "is_monitor",
                "is_mobile",
            ]
        )
        .agg(
            {
                "parameter_name": lambda x: ", ".join(sorted(set(x))),
                "sensor_id": lambda x: ", ".join(map(str, sorted(set(x)))),
            }
        )
        .reset_index()
    )

    grouped["color"] = grouped.apply(
        lambda row: [0, 200, 100] if "no" in row["parameter_name"] else [255, 100, 50],
        axis=1,
    )

    view_state = pdk.ViewState(
        latitude=grouped["latitude"].mean(),
        longitude=grouped["longitude"].mean(),
        zoom=12,
        pitch=0,
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=grouped,
        get_position=["longitude", "latitude"],
        get_color="color",
        get_radius=150,
        pickable=True,
    )

    tooltip = {
        "html": """
            <b>Station:</b> {name} <br/>
            <b>Locality:</b> {locality} <br/>
            <b>Owner:</b> {owner_name} <br/>
            <b>Source:</b> {provider_name} <br/>
            <b>Sensors IDs:</b> {sensor_id} <br/>
            <b>Is monitor:</b> {is_monitor} <br/>
            <b>Is Mobile:</b> {is_mobile} <br/>
            <b>Pollutants:</b> {parameter_name}
        """,
        "style": {"backgroundColor": "white", "color": "black", "font-size": "13px"},
    }

    st.pydeck_chart(
        pdk.Deck(
            map_style="road",
            initial_view_state=view_state,
            layers=[layer],
            tooltip=tooltip,  # type: ignore
        )
    )


def show_sensor_distribution(data: pd.DataFrame, sensors: pd.DataFrame):
    st.markdown("#### Sensor Distribution")
    st.caption("Distribution of measurements across different sensors/stations.")
    data = data.merge(sensors[["sensor_id", "name"]], on="sensor_id", how="left")
    data["sensor_id"] = data["sensor_id"].astype(str) + " - " + data["name"]

    sensor_counts = data["sensor_id"].value_counts().reset_index()
    sensor_counts.columns = ["sensor_id", "count"]
    # sensor_counts = sensor_counts.sort_values(by="count", ascending=False)

    bar_chart = (
        alt.Chart(sensor_counts)
        .mark_bar()
        .encode(
            x=alt.X("sensor_id:N", title="Sensor ID"),
            y=alt.Y("count:Q", title="Number of Measurements"),
            tooltip=["sensor_id:N", "count:Q"],
        )
        .properties(width=500, height=600, title="Measurements per Sensor/Station")
    )

    st.altair_chart(bar_chart, use_container_width=True)


def show_station_distribution(data: pd.DataFrame, sensors: pd.DataFrame):
    data = data.merge(sensors[["sensor_id", "name"]], on="sensor_id", how="left")
    data["sensor_id"] = data["sensor_id"].astype(str) + " - " + data["name"]

    st.altair_chart(
        alt.Chart(data)
        .mark_arc()
        .encode(
            alt.Theta("count()"),
            alt.Color(
                "name:N",
                scale=alt.Scale(
                    scheme="viridis"
                ),  # "category10", "tableau10", "set1", "dark2", "pastel1", "viridis", "plasma", "inferno", "magma".
                legend=alt.Legend(orient="bottom", direction ="vertical"),
            ),
        )
        .properties(width=700, height=300, title="Station Distribution")
    )


@st.cache_data
def load_data():
    start_date, end_date = get_dates_range(history_days=HIST_DAYS)
    data = read_db_between_dates(
        TABLE_NAME_MEASUREMENTS,
        date_column="datetime_from",
        start_date=start_date,
        end_date=end_date,
    )
    data["datetime_from"] = pd.to_datetime(data["datetime_from"])
    data["datetime_to"] = pd.to_datetime(data["datetime_to"])
    data["date"] = data["datetime_from"].dt.date
    return data


@st.cache_data
def load_sensors():
    data = read_db(TABLE_NAME_LOCATIONS)
    return data


def show_pollution_page(selected_days: tuple):
    df = load_data()
    sensors = load_sensors()

    if df.empty:
        st.warning("No air quality data available")
        return

    s_date, e_date = selected_days
    data = df[(df["date"] >= s_date) & (df["date"] <= e_date)].copy()

    # --- KPI Cards ---
    show_kpis(data)

    # plot_pollutants_over_time(data)

    # --- Air Quality Trends ---
    title = "Air Quality Trends"
    st.write(f"### {title}")
    list_pollutants = data.parameter_name.unique()
    pollutants = st.pills(
        "Select pollutant(s)",
        list_pollutants,
        default=list_pollutants,
        selection_mode="multi",
    )
    if not pollutants:
        st.error("Please select at least one pollutant.")

    filtered_data = data[data["parameter_name"].isin(pollutants)]

    cols = st.columns([3, 1])  # ---- Pollutant trends + sensor distribution ----
    with cols[0].container(border=True, height="stretch"):
        plot_pollutant_trends(filtered_data, pollutants)

    with cols[1].container(border=True, height="stretch"):
        show_station_distribution(filtered_data, sensors)

    cols = st.columns([1, 3])  #  --- Sensor map + sensor distribution ----
    with cols[0].container(border=True, height="stretch"):
        show_sensor_distribution(filtered_data, sensors)

    with cols[1].container(border=True, height="stretch"):
        show_sensor_map(sensors)

    cols = st.columns(2)  # ---- Heatmaps: pollutant by weekday + by sensor ----
    with cols[0].container(border=True, height="stretch"):
        heatmap_pollutant_weekday(filtered_data)

    with cols[1].container(border=True, height="stretch"):
        heatmap_pollutant_sensor(filtered_data)


def plot_pollutant_trends(data: pd.DataFrame, pollutants: list):
    title = "Pollutants Concentration Over Time"
    if len(pollutants) == 1:
        title = f"{pollutants[0].upper()} Concentration Over Time"
    # st.write(f"#### {title}")

    chart = (
        alt.Chart(data)
        .mark_area(opacity=0.3)
        .encode(
            x=alt.X("datetime_from:T", title="Date"),
            y=alt.Y("value:Q", stack=None, title="Concentration (µg/m³)"),
            color=alt.Color("parameter_name:N", title="Pollutant"),
            tooltip=["datetime_from:T", "value:Q", "parameter_units:N"],
        )
        .properties(title=title)
    )

    st.altair_chart(chart, use_container_width=True)


def show_kpis(data: pd.DataFrame):
    st.markdown("### Air Quality Key Indicators")
    st.caption(
        "Daily average values for each selected pollutant, compared with EU thresholds."
    )

    pollutants = data.parameter_name.unique()
    daily_means = data.groupby(["date", "parameter_name"])["value"].mean().reset_index()

    cols = st.columns(len(pollutants) + 1)
    ratios = []

    for i, pol in enumerate(pollutants):
        pol_data = daily_means[daily_means["parameter_name"] == pol]

        if pol_data.empty:
            cols[i].metric(
                label=f"{POLLUTANTS_INFO.get(pol, {}).get('nice_name', pol)} ({POLLUTANTS_INFO.get(pol, {}).get('unit', '')})",
                value="N/A",
                delta="No data",
            )
            continue

        limit = POLLUTANTS_LIMITS.get(pol)
        latest_value = pol_data["value"].iloc[-1]

        if limit and limit > 0:
            ratio = latest_value / limit
            ratios.append(ratio)
            status = "✅ Within limit" if latest_value <= limit else "⚠️ Above limit"
        else:
            ratio = np.nan
            status = "ℹ️ No defined threshold"

        cols[i].metric(
            label=f"{POLLUTANTS_INFO.get(pol, {}).get('nice_name', pol)} ({POLLUTANTS_INFO.get(pol, {}).get('unit', '')})",
            value=f"{latest_value:.2f}",
            delta=status,
        )

    # --- Global AQI-like based on ALL pollutants (average ratio) ---
    if ratios:
        mean_ratio = np.nanmean(ratios)
        aqi_score = round(mean_ratio * 100)

        if aqi_score < 50:
            aqi_label = "🟢 Good"
        elif aqi_score < 100:
            aqi_label = "🟠 Moderate"
        else:
            aqi_label = "🔴 Unhealthy"
    else:
        aqi_label = "N/A"
        aqi_score = None

    # KPI global AQI-like
    cols[len(pollutants)].metric(
        "Global AQI-like",
        f"{aqi_label}",
        f"{'' if aqi_score is None else aqi_score}%",
    )


def heatmap_pollutant_sensor(data: pd.DataFrame):
    """
    Display a heatmap of average pollutant concentration per sensor/station.
    """
    # Group by sensor and pollutant
    sensor_mean = (
        data.groupby(["sensor_id", "parameter_name"])["value"].mean().reset_index()
    )

    heatmap_sensor = (
        alt.Chart(sensor_mean)
        .mark_rect()
        .encode(
            x=alt.X("sensor_id:N", title="Sensor / Station"),
            y=alt.Y("parameter_name:N", title="Pollutant"),
            color=alt.Color("value:Q", title="Avg. Concentration (µg/m³)"),
            tooltip=["sensor_id:N", "parameter_name:N", "value:Q"],
        )
        .properties(
            width=700, height=300, title="Average Pollution by Sensor / Station"
        )
    )

    st.altair_chart(heatmap_sensor, use_container_width=True)


def heatmap_pollutant_weekday(data: pd.DataFrame):
    """
    Display a heatmap of average pollutant concentration by day of the week.
    """
    data["weekday"] = data["datetime_from"].dt.day_name()  # Monday, Tuesday, ...

    weekday_mean = (
        data.groupby(["weekday", "parameter_name"])["value"].mean().reset_index()
    )

    # Option pour ordonner les jours correctement
    days_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    weekday_mean["weekday"] = pd.Categorical(
        weekday_mean["weekday"], categories=days_order, ordered=True
    )

    heatmap_weekday = (
        alt.Chart(weekday_mean)
        .mark_rect()
        .encode(
            x=alt.X("weekday:N", title="Day of Week"),
            y=alt.Y("parameter_name:N", title="Pollutant"),
            color=alt.Color("value:Q", title="Avg. Concentration (µg/m³)"),
            tooltip=["weekday:N", "parameter_name:N", "value:Q"],
        )
        .properties(width=700, height=300, title="Average Pollution by Weekday")
    )

    st.altair_chart(heatmap_weekday, use_container_width=True)


def _prepare_sidebar():
    add_sidebar_title(title="SmartCity")
    st.sidebar.markdown(
        """
        Use the filters below to customize the data view.
        """
    )
    # show_all = st.sidebar.checkbox("Show all available days", value=False)
    st.sidebar.info("📅 Only data from the last 31 days is available.")

    today = date.today()
    min_day = today - timedelta(days=31)  # Available data range is last 31 days
    max_day = today
    default_start = today - timedelta(days=7)  # Default: last 7 days
    default_end = today

    selected_days = st.sidebar.date_input(
        "Select the days to display",
        value=(default_start, default_end),
        min_value=min_day,
        max_value=max_day,
    )

    if selected_days is None:
        filtered_start = filtered_end = today
    elif isinstance(selected_days, tuple):
        if len(selected_days) == 2:
            filtered_start, filtered_end = selected_days
        elif len(selected_days) == 1:
            filtered_start = filtered_end = selected_days[0]
        else:
            filtered_start = filtered_end = today
    else:
        filtered_start = filtered_end = selected_days

    # st.sidebar.write(f"Showing data from **{filtered_start}** to **{filtered_end}**")
    # st.sidebar.write(f"Showing data from **{selected_days}**.")

    return filtered_start, filtered_end

# ------- main --------
st.set_page_config(
    page_title="Air Quality",
    page_icon="🏙️",
    layout="wide",
)
st.markdown(
    """
    <div style="text-align: center; color: white; font-size: 18px; line-height: 1.6;">
        <h1>Air Quality in Clermont-Ferrand 🌱</h1>
        <p style="text-align: left;">
            Air quality directly affects our <strong>health and well-being</strong>.  
            This dashboard provides insights into air quality in Clermont-Ferrand.
            Data is collected from the <strong>OpenAQ API</strong> and refreshed daily.  <br>
            his dashboard provides insights into air quality in Clermont-Ferrand.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

selected_days = _prepare_sidebar()

show_pollution_page(selected_days)
