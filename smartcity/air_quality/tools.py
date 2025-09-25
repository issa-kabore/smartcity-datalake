import pandas as pd
from smartcity import logger


def clean_locations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and flattens a DataFrame of OpenAQ location objects.
    
    This function extracts nested attributes from columns like 'country', 
    'owner', 'provider', and 'sensors' into new, separate columns. It 
    uses vectorized operations and pandas' explode for efficiency.

    Args:
        df (pd.DataFrame): DataFrame containing OpenAQ Location objects.

    Returns:
        pd.DataFrame: A flattened DataFrame with one row per sensor.
    """
    logger.info("Cleaning and flattening location data ...")
    df_cleaned = df.copy()

    df_cleaned['country_id'] = df_cleaned['country'].apply(lambda x: x.id)
    df_cleaned['country_code'] = df_cleaned['country'].apply(lambda x: x.code)
    df_cleaned['country_name'] = df_cleaned['country'].apply(lambda x: x.name)

    def _split_column(df, column):
        df[f'{column}_id'] = df[column].apply(lambda x: x.id)
        df[f'{column}_name'] = df[column].apply(lambda x: x.name)
        return df

    for col in ['owner', 'provider']:
        df_cleaned = _split_column(df_cleaned, col)

    df_cleaned = df_cleaned.explode('sensors')
    df_cleaned['sensor_id'] = df_cleaned['sensors'].apply(lambda x: x.id)
    df_cleaned['sensor_name'] = df_cleaned['sensors'].apply(lambda x: x.name)
    df_cleaned['parameter_id'] = df_cleaned['sensors'].apply(lambda x: x.parameter.id)
    df_cleaned['parameter_name'] = df_cleaned['sensors'].apply(lambda x: x.parameter.name)
    df_cleaned['parameter_units'] = df_cleaned['sensors'].apply(lambda x: x.parameter.units)

    df_cleaned['latitude'] = df_cleaned['coordinates'].apply(lambda x: x.latitude if x else None)
    df_cleaned['longitude'] = df_cleaned['coordinates'].apply(lambda x: x.longitude if x else None)

    cols_to_drop = ['country', 'datetime_last', 'datetime_first', 'owner', 'provider', 'instruments', 'sensors', 'coordinates']
    logger.info("Location data cleaned and flattened.")
    return df_cleaned.drop(columns=cols_to_drop, errors='ignore')