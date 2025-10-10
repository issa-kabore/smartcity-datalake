import streamlit as st
from smartcity.st_ui import coming_soon, add_sidebar_title

# ------- main --------
st.set_page_config(
    page_title="Energy & Buildings",
    page_icon="🏙️",
    layout="wide",
)
add_sidebar_title(title="SmartCity")
coming_soon("Clermont-Ferrand Energy & Buildings",)