import os
from datetime import datetime, timedelta, timezone
from typing import List, Any, Optional, Tuple
import pandas as pd
import pendulum
from prefect.blocks.system import Secret


def get_secret(name: str, env_var: str):
    env = os.getenv("ENV")
    if env == "prod" or os.getenv("PREFECT__FLOW_RUN_ID"):
        return Secret.load(name).get()  # type: ignore
    return os.getenv(env_var)


def get_yesterday_utc_range():
    now_utc = datetime.now(timezone.utc)
    date_to = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    date_from = date_to - timedelta(days=2)
    return date_from.isoformat(), date_to.isoformat()


def get_yesterday_local_range(history_days=2):
    now_local = datetime.now()
    date_to = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    date_from = date_to - timedelta(days=history_days)
    return date_from.isoformat(), date_to.isoformat()


def get_dates_range(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    history_days: int = 1,
) -> Tuple[str, str]:
    """
    Determines the start and end dates based on the provided parameters.
    Args:
        start_date (Optional[str]): The start date in ISO 8601 format (e.g., "2023-10-01").
        end_date (Optional[str]): The end date in ISO 8601 format (e.g., "2023-10-02").
        history_days (int): Number of days to look back if only one date is provided. Default is 1.
    Returns:
        Tuple[str, str]: A tuple containing the start and end dates in ISO 8601 format in UTC.
    """
    if not start_date and not end_date:
        end_dt = pendulum.now(tz="UTC").start_of("day")
        start_dt = end_dt.subtract(days=history_days)

    elif start_date and not end_date:
        start_dt = pendulum.parse(start_date)
        end_dt = start_dt.add(days=history_days)  # type: ignore

    elif not start_date and end_date:
        end_dt = pendulum.parse(end_date)
        start_dt = end_dt.subtract(days=history_days)  # type: ignore

    else:
        start_dt = pendulum.parse(start_date)  # type: ignore
        end_dt = pendulum.parse(end_date)  # type: ignore

    if start_dt > end_dt:  # type: ignore
        raise ValueError("Error : start_date cannot be after end_date.")

    return start_dt.to_datetime_string(), end_dt.to_datetime_string()  # type: ignore


def get_attribute(obj: Any, attr_path: str, default=None):
    """Safely gets a nested attribute from an object, returning a default value if it doesn't exist."""
    attrs = attr_path.split(".")
    current_obj = obj
    try:
        for attr in attrs:
            current_obj = getattr(current_obj, attr)
        return current_obj
    except (AttributeError, TypeError):
        return default


def flatten_and_transform(
    data_list: List[Any], attributes: List[str] = list()
) -> pd.DataFrame:
    """
    Transforms a list of OpenAQ objects into a pandas DataFrame.

    Args:
        data_list (List[Any]): A list of objects from the OpenAQ API (e.g., Location, Measurement).
        attributes (List[str]): A list of attributes to extract, using dot notation for nested attributes.

    Returns:
        pd.DataFrame: A DataFrame with the flattened data.
    """
    flattened_data = []
    attributes = list(data_list[0].__dict__.keys()) if not attributes else attributes
    for item in data_list:
        row_data = {}
        for attr in attributes:
            # Generate a clean column name for the attribute
            col_name = attr.replace(".", "_")
            row_data[col_name] = get_attribute(item, attr)
        flattened_data.append(row_data)

    return pd.DataFrame(flattened_data)
