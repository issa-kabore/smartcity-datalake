import pandas as pd

from smartcity.database import (
    delete_old_measurements,
    upload_logs_to_supabase,
    upsert_measurements,
    TABLE_NAME_MEASUREMENTS,
)
from smartcity.air_quality.openaq_api import fetch_openaq_data

from prefect import task


@task(retries=3, retry_delay_seconds=10)
def fetch_openaq() -> pd.DataFrame:
    """Fetch air quality data from OpenAQ API"""
    data = fetch_openaq_data()
    return data


@task(retries=3, retry_delay_seconds=10)
def insert_openaq_data(df: pd.DataFrame):
    upsert_measurements(df)


@task(retries=3, retry_delay_seconds=10)
def cleanup_table(days: int = 30):
    delete_old_measurements(days=days, table_name=TABLE_NAME_MEASUREMENTS)


@task(retries=2, retry_delay_seconds=15)
def upload_logs():
    upload_logs_to_supabase(remote_name="workflow_openaq.log")
