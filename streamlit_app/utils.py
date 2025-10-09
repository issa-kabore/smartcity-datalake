import streamlit as st
import os

WEATHER_ICONS = {
    "sun": "☀️",
    "snow": "☃️",
    "rain": "💧",
    "fog": "😶‍🌫️",
    "drizzle": "🌧️",
}

POLLUTANTS_INFO = {
    "no": {"nice_name": "NO", "unit": "µg/m³"},
    "no2": {"nice_name": "NO₂", "unit": "µg/m³"},
    "pm10": {"nice_name": "PM10", "unit": "µg/m³"},
    "pm25": {"nice_name": "PM2.5", "unit": "µg/m³"},
    "o3": {"nice_name": "O₃", "unit": "µg/m³"},
}

POLLUTANTS_LIMITS = {"no2": 40, "o3": 100, "pm10": 50, "pm25": 25}


def coming_soon(title: str, message: str = "This page is under construction."):
    st.title(title)
    st.info(f"🚧 {message} Coming soon!")


def add_sidebar_title(title: str = "SmartCity Dashboard"):
    st.markdown(
        """
    <style>
        [data-testid="stSidebarNav"] {{
            padding-top: 10px;
        }}
        [data-testid="stSidebarNav"]::before {{
            content: "{title}";
            display: block;
            text-align: center;
            font-family: var(--font-title);
            font-weight: 600;
            color: var(--text-primary);
            font-size: 1.5rem;
            margin-top: 0px;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #9A6BFF 0%, #F254A4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
    </style>
    """.format(
            title=title
        ),
        unsafe_allow_html=True,
    )
