import sys
import os
import base64
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from smartcity.st_ui import add_sidebar_title


def set_background(img_file: str, ext: str = "jpg"):
    with open(img_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url(data:image/{ext};base64,{encoded});
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def run():
    st.set_page_config(
        page_title="SmartCity Dashboard",
        layout="centered",
        page_icon="🏙️",
    )
    add_sidebar_title(title='SmartCity')

    # set_background("streamlit_app/assets/Background-clf.jpg")
    st.write(
    """
    <div style="background-color: rgba(192,0,0,0.85); padding: 20px; border-radius: 10px; color: white;">
        <h2>Welcome to SmartCity Dashboard 👋</h2>
    </div>
    """,
    unsafe_allow_html=True
    )

    st.sidebar.success("Select a page above.")
    st.markdown(
        """
    <div style="background-color: rgba(255,255,255,0.8); padding: 30px; border-radius: 10px; color: black;">
        Discover data-driven insights about <strong>Clermont-Ferrand</strong>.  <br>
        Use the navigation menu to explore air quality, weather, real estate, and energy.  <br><br>

    <h4>Useful links</h4>
    <ul>
        <li><a href="https://clermont-ferrand.fr/" target="_blank">City of Clermont-Ferrand Official Website</a></li>
        <li><a href="https://openaq.org" target="_blank">OpenAQ Air Quality Data</a></li>
        <li><a href="https://meteofrance.com" target="_blank">Météo France</a></li>
        <li><a href="https://www.insee.fr" target="_blank">INSEE Statistics</a></li>
    </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    run()
