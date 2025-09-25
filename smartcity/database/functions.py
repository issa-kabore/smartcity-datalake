import pandas as pd
from supabase import create_client, Client
from smartcity.config import SUPABASE_URL, SUPABASE_KEY, TABLE_NAME_MEASUREMENTS
from smartcity import logger

UNIQUE_MEASUREMENT = "parameter_name,parameter_units,datetime_from,datetime_to,sensor_id"

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
    """"Retrieves all records from a specified Supabase table and returns them as a pandas DataFrame."""
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

        logger.info(f"> Upserted '{len(response.data)}' new records into '{TABLE_NAME_MEASUREMENTS}'.")

        return response.data

    except Exception as e:
        logger.error(f"Error upserting measurements to Supabase: {e}")
        raise e

