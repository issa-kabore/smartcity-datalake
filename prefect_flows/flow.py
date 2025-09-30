import pandas as pd

import smartcity
from smartcity.database import upload_logs_to_supabase, upsert_measurements
from smartcity.air_quality.openaq_api import fetch_openaq_data

from prefect import flow, tags, task, get_run_logger


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
    logger = get_run_logger()
    logger.info("Starting SmartCity OpenAQ ETL flow ...")
    logger.info(f">>> {smartcity.__version__ =  }")
    df = fetch_openaq_data()
    logger.info(f"> Air quality measurements Fetched !")
    if df.empty:
        logger.warning("No data fetched from OpenAQ.")
        return

    upsert_measurements(df)
    logger.info(f"> Air quality measurements Upserts !")

    upload_logs_to_supabase(remote_name="workflow_openaq.log")
    logger.info(f"> Logs Uploaded !")
