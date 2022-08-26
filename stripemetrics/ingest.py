import stripe
import pandas as pd
import numpy as np
from stripemetrics.date_manipulation import date_columns_names
from types import FunctionType


def get_data(
    resource: str,
    api_key: str,
    start_date: str = None,
    end_date: str = None,
    date_hour_type: FunctionType = None,
    api_version: str = None,
    **kwargs
) -> pd.DataFrame:
    """
    Get a certain resource from stripe api, returns it as a pandas DataFrame.

    Parameters
    ----------
    resource : str
        a stripe resource/table such as Charge, Subscription, Product
    api_key : str
        a key with read access to the stripe API
    start_date : str, default None
        a date of form 'YYYY/MM/DD'
    end_date : str, default None
        a date of form 'YYYY/MM/DD'
    date_hour_type : FunctionType, default None
        a function that changes the behaviour of the date and hours
    api_version : str, default None
    **kwargs
        arbitrary keyword arguments

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with the request stripe data
    """
    stripe.api_key = api_key

    if api_version:
        stripe.api_version = api_version
    if start_date:
        start_date = int(pd.Timestamp(start_date))
    if end_date:
        end_date = int(pd.Timestamp(start_date))

    resource_list = getattr(stripe, resource).list(limit=100, created={"gte": start_date, "lt": end_date}, **kwargs)
    lst = [resource for resource in resource_list.auto_paging_iter()]

    df = pd.DataFrame(lst)
    if len(df) > 0:
        mask = [col in date_columns_names for col in df.columns]
        date_columns = list(np.array(df.columns)[mask])

        df[date_columns] = df[date_columns].apply(
            pd.to_datetime, unit='s'
        )

    if date_hour_type:
        for date_column in date_columns:
            df[date_column] = df[date_column].apply(date_hour_type)

    return df