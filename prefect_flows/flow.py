import pandas as pd

import smartcity
from smartcity.database.functions import upsert_measurements
from smartcity.air_quality.openaq_api import fetch_openaq_data

from prefect import flow, tags, task
from prefect.logging import get_run_logger


@task(retries=3, retry_delay_seconds=10)
def fetch_openaq() -> pd.DataFrame:
    """Fetch air quality data from OpenAQ API"""
    data = fetch_openaq_data()
    return data


@flow(name="SmartCity OpenAQ ETL", log_prints=True)
def workflow_openaq():
    """
    ETL flow: fetch air quality data from OpenAQ and upsert into Supabase.
    Designed to run daily via Prefect Cloud.
    """
    log = get_run_logger()
    log.info("Starting SmartCity OpenAQ ETL flow ...")
    log.info(f">>> {smartcity.__version__ =  }")
    df = fetch_openaq_data()
    if df.empty:
        log.warning("No data fetched from OpenAQ.")
        return

    upsert_measurements(df)
