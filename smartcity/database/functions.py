import os
import re
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
from smartcity.config import SUPABASE_URL, SUPABASE_KEY, TABLE_NAME_MEASUREMENTS
from smartcity import logger, LOG_FILE_PATH

UNIQUE_MEASUREMENT = (
    "parameter_name,parameter_units,datetime_from,datetime_to,sensor_id"
)


def load_to_supabase(df: pd.DataFrame, table_name: str) -> None:
    """
    Loads a pandas DataFrame into a specified Supabase table.

    This function is a core part of the 'Load' step in your data pipeline.
    It securely connects to your Supabase database and inserts data
    in a format optimized for the service.

    Args:
        df (pd.DataFrame): The DataFrame to be loaded.
        table_name (str): The name of the target table in Supabase.
    """
    logger.info(f"Loading data into Supabase table '{table_name}' ...")
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Supabase credentials not found in environment variables.")

        # Initialize the Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Convert the DataFrame to a list of dictionaries, which is the format
        # required by Supabase's insert method.
        data = df.to_dict(orient="records")
        response = supabase.table(table_name).insert(data).execute()
        logger.info(
            f"Successfully loaded {len(response.data)} records into '{table_name}'."
        )

    except Exception as e:
        logger.error(f"Error loading data to Supabase: {e}")
        raise e


def read_db(table_name: str) -> pd.DataFrame:
    """ "Retrieves all records from a specified Supabase table and returns them as a pandas DataFrame."""
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Supabase credentials not found in environment variables.")
        logger.debug(f"Retrieving all data from Supabase table '{table_name}' ...")

        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.debug(">>> Supabase client initialized.")
        response = supabase.table(table_name).select("*").execute()

        if response.data:
            df = pd.DataFrame(response.data)
            logger.info(f"Successfully retrieved '{len(df)}' rows from '{table_name}'.")
            return df
        else:
            logger.warning(f"No data found in table '{table_name}'.")
            return pd.DataFrame()

    except Exception as e:
        logger.error(f"Error retrieving data from Supabase: {e}")
        raise e


def upsert_measurements(data: pd.DataFrame) -> list[dict]:
    """
    Upserts air quality measurements into the Supabase table.

    This function inserts or updates rows in the Supabase `openaq_measurements` table
    using the unique constraint defined in `UNIQUE_MEASUREMENT`.

    Args:
        data (pd.DataFrame): DataFrame containing the measurements to upsert.
            Expected columns: [
                'parameter_name', 'value', 'parameter_units',
                'datetime_from', 'datetime_to', 'period',
                'summary', 'percent_coverage', 'sensor_id', 'updated_at'
            ]

    Returns:
        list[dict]: List of records returned by Supabase after the upsert

    Raises:
        Exception: If the Supabase upsert request fails.
    """
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)  # type: ignore
    measurements = data.to_dict(orient="records")

    try:
        response = (
            supabase.table(TABLE_NAME_MEASUREMENTS)
            .upsert(
                measurements,
                on_conflict=UNIQUE_MEASUREMENT,
            )
            .execute()
        )

        logger.info(
            f"> Upserted '{len(response.data)}' new records into '{TABLE_NAME_MEASUREMENTS}'."
        )

        return response.data

    except Exception as e:
        logger.error(f"Error upserting measurements to Supabase: {e}")
        raise e


def upload_logs_to_supabase(
    log_file: str = "",
    bucket_name: str = "data",
    remote_dir: str = "smartcity-logs",
    remote_name: str = "",
    upsert: bool = True,
) -> str:
    """
    Upload a local log file to Supabase Storage.

    Args:
        log_file (str): Local log file path. Defaults to LOG_FILE_PATH if empty.
        bucket_name (str): Supabase bucket name.
        remote_dir (str): Folder inside the bucket.
        remote_name (str): If provided, overrides the default name generation.
        upsert (bool): Overwrite existing file if True.

    Returns:
        str: Remote path of the uploaded log file.
    """
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)  # type: ignore
    src_file = log_file or LOG_FILE_PATH

    if not os.path.exists(src_file):
        raise FileNotFoundError(f"Log file not found: {src_file}")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if remote_name:
        base = os.path.splitext(os.path.basename(remote_name))[0]  # sans extension
    else:
        base = os.path.splitext(os.path.basename(src_file))[0]

    final_name = f"{base}_{timestamp}.log"
    remote_path = f"{remote_dir}/{final_name}"

    rotate_logs_supabase(supabase, bucket_name, remote_dir, remote_name)

    try:
        with open(src_file, "rb") as f:
            supabase.storage.from_(bucket_name).upload(
                path=remote_path,
                file=f,
                file_options={"upsert": str(upsert).lower()},
            )
        logger.info(f"Log file uploaded to '{bucket_name}/{remote_path}'")

        return remote_path
    except Exception as e:
        logger.error(f"Failed to upload log file '{src_file}' → {e}")
        raise e


def rotate_logs_supabase(
    supabase: Client,
    bucket_name: str,
    remote_dir: str,
    remote_name: str,
    keep_last: int = 3,
):
    """
    Rotate log files stored in a Supabase storage bucket by keeping only the most recent ones.

    This function scans the given directory inside a Supabase storage bucket for 
    log files matching a specific naming pattern (e.g., `workflow_openaq_YYYY-MM-DD_HH-MM-SS.log`). 
    It sorts the logs by their last modification time, keeps the most recent `keep_last` logs, 
    and deletes the older ones.

    Args:
        supabase (Client): An authenticated Supabase client.
        bucket_name (str): The name of the Supabase storage bucket.
        remote_dir (str): The directory inside the bucket where log files are stored.
        remote_name (str): Base log filename (e.g., "workflow_openaq.log"). 
            The rotated files are expected to follow the pattern `<base>_YYYY-MM-DD_HH-MM-SS.log`.
        keep_last (int, optional): Number of most recent log files to keep. Defaults to 3.

    Example:
        >>> rotate_logs_supabase(
        ...     supabase=my_client,
        ...     bucket_name="data",
        ...     remote_dir="smartcity-logs",
        ...     remote_name="workflow_openaq.log",
        ...     keep_last=5,
        ... )
        # Keeps 5 most recent logs and deletes older ones.

    Notes:
        - The function assumes that log files contain a timestamp suffix in the format 
          `YYYY-MM-DD_HH-MM-SS`.
        - Requires that Supabase storage API provides `metadata['lastModified']`.
    """
    base = remote_name.replace(".log", "")
    pattern = re.compile(
        rf"^{base}_(\d{{4}}-\d{{2}}-\d{{2}}_\d{{2}}-\d{{2}}-\d{{2}})\.log$"
    )

    files = supabase.storage.from_(bucket_name).list(remote_dir)
    log_files = [f for f in files if pattern.match(f["name"])]
    log_files.sort(key=lambda x: x["metadata"]["lastModified"], reverse=True)  # type: ignore
    to_delete = log_files[keep_last:]

    for f in to_delete:
        supabase.storage.from_(bucket_name).remove([f"{remote_dir}/{f.get('name')}"])
        logger.debug(f"Deleted old log file: {f.get('name')}")

    logger.info(f"Rotation done. Kept '{keep_last}', deleted {len(to_delete)}.")
