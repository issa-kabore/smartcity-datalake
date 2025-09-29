from datetime import datetime
from typing import List
from openaq import OpenAQ
import pandas as pd

from smartcity.config import OPENAQ_API_KEY, TABLE_NAME_LOCATIONS
from smartcity.logger import get_smartcity_logger
from smartcity.database.functions import read_db
from smartcity.utils import flatten_and_transform, get_dates_range, get_yesterday_local_range


logger = get_smartcity_logger()

def fetch_locations(
    client: OpenAQ, country_code: str = "US", limit: int = 100
) -> pd.DataFrame:
    """
    Fetch locations from OpenAQ API for a given city and country.

    Args:
        city (str): The city to fetch locations for.
        country_code (str): The country code (default is "US").
        limit (int): The maximum number of locations to fetch (default is 100).
    Returns:
        pd.DataFrame: DataFrame containing location data.
    """
    locations = client.locations.list(limit=limit, iso=country_code)
    locations = flatten_and_transform(locations.results)
    return locations


def flatten_measurements(measurements: list) -> pd.DataFrame:
    """
    Transforms a list of OpenAQ Measurement objects into a pandas DataFrame.

    Args:
        measurements (list): A list of Measurement objects from the OpenAQ API.

    Returns:
        pd.DataFrame: A DataFrame with the flattened measurement data.
    """
    flattened_data = []
    for m in measurements:
        flat_dict = {
            "parameter_name": m.parameter.name,
            "value": m.value,
            "parameter_units": m.parameter.units,
            "datetime_from": m.period.datetime_from.local,
            "datetime_to": m.period.datetime_to.local,
            "period": m.period.interval,
            # "coord": m.coordinates,
            "summary": m.summary,
            "percent_coverage": m.coverage.percent_coverage,
        }
        flattened_data.append(flat_dict)
    return pd.DataFrame(flattened_data)


def fetch_sensor_measurements(
    client: OpenAQ, sensor_id: int, date_from: str, date_to: str, limit: int = 1000
) -> pd.DataFrame:
    """
    Fetches air quality measurements from the OpenAQ API for a specific location ID
    within a given date range.

    Args:
        client (OpenAQ): An initialized OpenAQ client.
        sensor_id (int): The ID of the sensor/location to fetch measurements for.
        date_from (str): The start date in 'YYYY-MM-DD' format.
        date_to (str): The end date in 'YYYY-MM-DD' format.
        limit (int): Maximum number of records to fetch. Default is 10,000.

    Returns:
        pd.DataFrame: A DataFrame containing the fetched measurements.
    """
    try:
        logger.debug(f"> Fetching measurements for Sensor ID '{sensor_id}' ...")
        response = client.measurements.list(
            sensors_id=sensor_id,
            datetime_from=date_from,
            datetime_to=date_to,
            limit=limit,
        )
        if response and response.results:
            df = flatten_measurements(response.results)
            logger.debug(f"> Fetched '{len(df)}' records.")
            return df
        else:
            logger.warning(f"> No measurements found (for sensor ID : {sensor_id}).")
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"> Error fetching measurements: {e}")
        raise e


def fetch_measurements(list_sensors: List[int], date_from, date_to) -> pd.DataFrame:
    client: OpenAQ = OpenAQ(api_key=OPENAQ_API_KEY)
    logger.info(">>> OpenAQ client initialized")

    logger.info("Fetching measurements from OpenAQ ...")
    logger.info(f"From '{date_from}' to '{date_to}' ...")
    measurements_df = pd.DataFrame()
    for sensor_id in list_sensors:
        df = fetch_sensor_measurements(
            client=client, sensor_id=sensor_id, date_from=date_from, date_to=date_to
        )
        if not df.empty:
            df["sensor_id"] = sensor_id
            df["updated_at"] = datetime.now().isoformat()

        measurements_df = pd.concat([measurements_df, df], ignore_index=True)

    logger.info(f"Fetched total '{len(measurements_df)}' measurements.")
    logger.debug(
        f"Missing sensor IDs: {set(list_sensors) - set(measurements_df['sensor_id'])}"
    )
    if measurements_df.empty:
        logger.warning("No measurements were fetched.")

    client.close()
    logger.info(">>> OpenAQ client closed !!!")
    return measurements_df


def fetch_openaq_data() -> pd.DataFrame:
    """Fetch air quality data from OpenAQ API"""
    date_from, date_to = get_dates_range(history_days=7)

    sensors_info = read_db(table_name=TABLE_NAME_LOCATIONS)
    logger.info(f"Fetched '{sensors_info['sensor_id'].nunique()}' sensors from DB.")

    data = fetch_measurements(list_sensors=sensors_info["sensor_id"].unique().tolist(),
                              date_from=date_from, date_to=date_to)
    data = data.drop_duplicates(ignore_index=True)
    return data