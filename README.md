# SmartCity Datalake
SmartCity Datalake is an open-source project designed to centralize, store, and analyze public city-related data (with a first focus on Clermont-Ferrand).
The main goal is to build a free and reproducible platform that enables:
- Ingestion of open data (public Wi-Fi, green spaces, sports facilities, CO₂ reports, etc.).
- Storage in a structured datalake.
- Access for data analysis, data science, and generative AI (via RAG).


## Draft Project Structure
    smartcity-datalake/
    │── data/                # Raw & processed datasets
    │── flows/               # Prefect flows (ingestion, transformation)
    │── notebooks/           # Jupyter notebooks for exploration
    │── app/                 # Streamlit app (chatbot, visualization)
    │── configs/             # Configuration files (Prefect, MinIO, etc.)
    │── tests/               # Unit tests
    │── README.md
