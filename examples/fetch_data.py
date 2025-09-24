import os
import logging

from smartcity import logger
from smartcity.config import TABLE_NAME_LOCATIONS
from smartcity.utils import get_dates_range
from smartcity.database.functions import read_db, upsert_measurements
from smartcity.air_quality.openaq_api import fetch_measurements
from smartcity.air_quality.tools import clean_locations



if __name__ == "__main__":
    # logger.setLevel(logging.DEBUG)
    date_from, date_to = get_dates_range(history_days=7)

    sensors_info = read_db(table_name=TABLE_NAME_LOCATIONS)
    logger.info(f"Fetched '{sensors_info["sensor_id"].nunique()}' sensors from DB.")

    data = fetch_measurements(list_sensors=sensors_info["sensor_id"].unique().tolist(),
                              date_from=date_from, date_to=date_to)
    data = data.drop_duplicates(ignore_index=True)
    logger.info(f"Columns: {data.columns.tolist()}")
    logger.info(f"{data.shape = }")
    # data.to_csv(os.path.join("data", "raw", "openaq_measurements.csv"), index=False)
    # upsert_measurements(data)