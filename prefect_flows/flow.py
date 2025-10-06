from prefect_flows.task import (
    fetch_openaq,
    insert_openaq_data,
    cleanup_table,
    upload_logs_to_supabase,
)
import smartcity

from prefect import flow, task, get_run_logger


@flow(name="SmartCity OpenAQ ETL", log_prints=True)
def workflow_openaq():
    """
    Prefect Flow: SmartCity OpenAQ ETL

    This flow automates the end-to-end process of collecting and maintaining air quality data 
    from the OpenAQ API and storing it in the Supabase database.

    Steps:
        1. **Fetch data** — Retrieve the latest air quality measurements from OpenAQ.
        2. **Upsert data** — Insert or update measurements in the Supabase table.
        3. **Cleanup old records** — Delete data older than 30 days to keep storage optimized.
        4. **Upload logs** — Push local log files to Supabase Storage for audit and traceability.

    This flow is designed to run daily via Prefect Cloud (scheduled or automated), 
    ensuring the SmartCity data lake remains up-to-date and clean.

    Returns:
        None

    Notes:
        - Retries are applied to each task (3 attempts, 10s delay).
        - Logs are automatically uploaded after each successful run.
        - Can be monitored and orchestrated entirely from the Prefect UI.
    """
    logger = get_run_logger()
    logger.info("Starting SmartCity OpenAQ ETL flow ...")
    logger.info(f">>> {smartcity.__version__ =  }")

    df = fetch_openaq()
    logger.info(f"> Air quality measurements Fetched !")
    if df.empty:
        logger.warning("No data fetched from OpenAQ.")
        return

    insert_openaq_data(df)
    logger.info(f"> Air quality measurements Upserted successfully.")

    cleanup_table(days=30)
    logger.info(f"> Old measurements (< 30 days) deleted successfully.")

    upload_logs_to_supabase(remote_name="workflow_openaq.log")
    logger.info(f"> Logs uploaded to Supabase.")

    logger.info("SmartCity OpenAQ ETL flow completed.")
