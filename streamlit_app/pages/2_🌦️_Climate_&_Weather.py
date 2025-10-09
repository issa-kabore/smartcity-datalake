import streamlit as st
from utils import coming_soon, add_sidebar_title


# ------- main --------
st.set_page_config(
    page_title="Climate & Weather",
    page_icon="🏙️",
    layout="wide",
)
add_sidebar_title(title="SmartCity")
coming_soon("Clermont-Ferrand Weather 🌦️", "Live climate and weather insights will be available here. This page is under construction.")
st.caption("Stay tuned for live climate and weather insights across Clermont-Ferrand.")