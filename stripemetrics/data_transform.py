import pandas as pd
from .date_manipulation import _last_interval_days
import numpy as np


def enrich_subscriptions(
        sub_df: pd.DataFrame,
        prod_df: pd.DataFrame or None = None
) -> pd.DataFrame:
    """
    Extract plan and coupon information from Subscription DataFrame.
    If Product DataFrame is provided, also enrich the resulting DataFrame with product information.

    Plan Information:
        plan_amount, plan_interval, product
    Coupon Information:
        percent_off, duration
    Product Information
        name

    Parameters
    ----------
    sub_df : DataFrame
        Stripe Subscription DataFrame
    prod_df : DataFrame or None, default None
        Stripe Product DataFrame

    Returns
    -------
    pd.DataFrame
        Subscription Pandas DataFrame enriched with more information
    """
    subs_enriched = sub_df.copy()
    subs_enriched = subs_enriched[~subs_enriched['plan'].isna()]

    subs_enriched['plan_amount'] = subs_enriched['plan'].map(lambda x: x['amount'])
    subs_enriched['plan_interval'] = subs_enriched['plan'].map(lambda x: x['interval'])
    subs_enriched['product'] = subs_enriched['plan'].map(lambda x: x['product'])

    subs_enriched['percent_off'] = subs_enriched['discount'].map(
        lambda x: x['coupon']['percent_off'] if x is not None else 0)
    subs_enriched['coupon_duration'] = subs_enriched['discount'].map(
        lambda x: x['coupon']['duration'] if x is not None else 0)

    if prod_df is not None:
        # merging to get product information
        subs_enriched = pd.merge(subs_enriched, prod_df[['id', 'name']].rename(columns={'id': 'product_id'}),
                                 left_on='product', right_on='product_id').drop('product', axis=1)

    return subs_enriched


def enrich_charges(
        ch_df: pd.DataFrame,
        prod_df: pd.DataFrame,
        balance_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Enrich Charge DataFrame with Product and Balance Transaction information.

    Product Information:
        product_key, name
    Balance Information:
        currency, exchange_rate, source, type

    Parameters
    ----------
    ch_df : pd.DataFrame
        Stripe Charge DataFrame
    prod_df : pd.DataFrame
        Stripe Product DataFrame
    balance_df : pd.DataFrame
        Stripe Balance Transaction Information

    Returns
    -------
    pd.DataFrame
        Charge Pandas DataFrame enriched with Product and Balance Transaction information
    """
    charges_enriched = ch_df.copy()
    charges_enriched['product_key'] = charges_enriched.apply(
        lambda x: x['metadata']['product_key'] if 'product_key' in x['metadata'].keys() is not None else np.nan, axis=1).astype('category')

    charges_enriched = pd.merge(charges_enriched, balance_df[['currency', 'exchange_rate', 'source', 'type']],
                                how='left', left_on='id', right_on='source', suffixes=('', '_bal'))

    charges_enriched['exchange_rate'] = charges_enriched['exchange_rate'].fillna(1)
    charges_enriched['amount_captured_usd'] = (charges_enriched['amount_captured'] * charges_enriched[
        'exchange_rate']) / 100

    charges_enriched = pd.merge(charges_enriched, prod_df[['id', 'name']].rename(columns={'id': 'product_id'}),
                                left_on='product_key', right_on='product_id', how='left').drop('product_key', axis=1)

    return charges_enriched


def active_subscriptions(
        sub_df: pd.DataFrame,
        date: str,
        product: str or None = None,
        interval: int = 30
) -> pd.Series:
    """
    Get id of active subscriptions in the last interval (default 30) days starting from date ('YYYY/MM/DD').
    If product name is provided, filter subscriptions by product (Subscription must be enriched with product data).

    Parameters
    ----------
    sub_df : pd.DataFrame
        Stripe Subscription DataFrame
    date : str
        A date of format 'YYYY/MM/DD'
    product : str or None, default None
        Name of a Stripe product
    interval : int, default 30
        Amount of days in the past to check

    Returns
    -------
    pd.Series
        Pandas Series containing the ids of active subscriptions
    """
    # if product is not None, enrich_subscriptions is needed
    date = pd.Timestamp(date)
    next_date = date + pd.Timedelta(days=interval)
    df = sub_df.copy()

    active_subs = df[
        (df['created'] < date) &
        ((df['canceled_at'] > date) | pd.isnull(df['canceled_at'])) &
        ((df['cancel_at'] > date) | pd.isnull(df['cancel_at'])) &
        ((df['trial_end'] < next_date) | pd.isnull(df['trial_end']))
        ]

    if (product is not None) and ('name' in active_subs.columns):
        active_subs = active_subs[active_subs['name'] == product]

    return active_subs['id']


def active_subscribers(
        sub_df: pd.DataFrame,
        date: str,
        product: str or None = None,
        interval: int = 30
) -> pd.Series:
    """
    Get id of active subscribers in the last interval (default 30) days starting from date ('YYYY/MM/DD').
    If product name is provided, filter subscribers by product (Subscription must be enriched with product data).

    Parameters
    ----------
    sub_df : pd.DataFrame
        Stripe Subscription DataFrame
    date : str
        A date of format 'YYYY/MM/DD'
    product : str or None, default None
        Name of a Stripe product
    interval : int, default 30
        Amount of days in the past to check

    Returns
    -------
    pd.Series
        Pandas Series containing the ids of active subscribers
    """
    # if product is not None, enrich_subscriptions is needed
    subscriptions = active_subscriptions(sub_df, date, product, interval)
    df = sub_df.copy()

    subscribers = df[df['id'].isin(subscriptions)]['customer']
    unique_subs = subscribers.unique()

    return pd.Series(unique_subs)


def new_subscribers(
        sub_df: pd.DataFrame,
        date: str,
        product: str or None = None,
        interval: int = 30
) -> pd.Series:
    """
    Get id of new subscribers in the last interval (default 30) days starting from date ('YYYY/MM/DD').
    If product name is provided, filter subscribers by product (Subscription must be enriched with product data).

    Parameters
    ----------
    sub_df : pd.DataFrame
        Stripe Subscription DataFrame
    date : str
        A date of format 'YYYY/MM/DD'
    product : str or None, default None
        Name of a Stripe product
    interval : int, default 30
        Amount of days in the past to check

    Returns
    -------
    pd.Series
        Pandas Series containing the ids of new subscribers
    """
    df = sub_df.copy()
    date, last_date = _last_interval_days(date, interval)

    if product:
        # enrich_subscriptions is needed
        df = df[df['name'] == product]

    prev_active_subscribers = active_subscribers(sub_df, last_date, product)
    cur_active_subscribers = active_subscribers(sub_df, date, product)

    prev = set(sub_df[sub_df['customer'].isin(prev_active_subscribers)]['customer'].unique())
    cur = set(sub_df[sub_df['customer'].isin(cur_active_subscribers)]['customer'].unique())

    # in current and not in previous
    # note: should also check whether the new subscriber was subscribed once in the past
    return pd.Series(list(cur - prev), dtype=pd.StringDtype())


def new_subscriptions(
        sub_df: pd.DataFrame,
        date: str,
        product: str or None = None,
        interval: int = 30
):
    """
    Get id of new subscriptions in the last interval (default 30) days starting from date ('YYYY/MM/DD').
    If product name is provided, filter subscriptions by product (Subscription must be enriched with product data).

    Parameters
    ----------
    sub_df : pd.DataFrame
        Stripe Subscription DataFrame
    date : str
        A date of format 'YYYY/MM/DD'
    product : str or None, default None
        Name of a Stripe product
    interval : int, default 30
        Amount of days in the past to check

    Returns
    -------
    pd.Series
        Pandas Series containing the ids of new subscriptions
    """
    # if product is not None, enrich_subscriptions is needed
    date, last_date = _last_interval_days(date, interval)

    prev_active_subscriptions = active_subscriptions(sub_df, last_date, product)
    cur_active_subscriptions = active_subscriptions(sub_df, date, product)

    prev = set(sub_df[sub_df['id'].isin(prev_active_subscriptions)]['id'].unique())
    cur = set(sub_df[sub_df['id'].isin(cur_active_subscriptions)]['id'].unique())

    # in current and not in previous
    return pd.Series(list(cur - prev), dtype=pd.StringDtype())


def churn_dates(
        sub_df: pd.DataFrame,
        date: str or None = None,
        product: str or None = None,
        interval: int = 30
) -> pd.DataFrame:
    """
    Get the churn date for subscribers that canceled in the last interval (default 30) days, return a DataFrame
    containing dates and ids.

    The parameter for date narrows the date interval to check.
    If product name is provided, filters subscriptions by product (Subscription must be enriched with product data).

    Parameters
    ----------
    sub_df : pd.DataFrame
        Stripe Subscription DataFrame
    date : str
        A date of format 'YYYY/MM/DD'
    product : str or None, default None
        Name of a Stripe product
    interval : int, default 30
        Amount of days in the past to check

    Returns
    -------
    pd.DataFrame
        dataframe with subscriber ids and their respective churn dates
    """
    df = sub_df.copy()
    if date is not None:
        date, last_date = _last_interval_days(date, interval)
        df = df[(df['canceled_at'] > last_date) &
                (df['canceled_at'] < date)]

    if product is not None:
        # enrich_subscriptions is needed
        df = df[df['name'] == product]

    customers = df['customer'].unique()

    churn_dates = []
    for customer_id in customers:
        subscriber_df = df[df['customer'] == customer_id]
        churn_date = pd.NaT

        if ('active' not in subscriber_df['status']) and ('past_due' not in subscriber_df['status']):
            churn_date = subscriber_df[subscriber_df['status'] == 'canceled']['canceled_at'].max()

        churn_dates.append(churn_date)

    customer_churn_dates = pd.DataFrame({'customer': customers, 'churn date': churn_dates})

    return customer_churn_dates


def subscription_churn_dates(
        sub_df: pd.DataFrame,
        date: str or None = None,
        product: str or None = None,
        interval: int = 30
) -> pd.DataFrame:
    """
    Get the churn date for subscriptions that canceled in the last interval (default 30) days, return a DataFrame
    containing dates and ids.

    The parameter for date narrows the date interval to check.
    If product name is provided, filter subscriptions by product (Subscription must be enriched with product data).

    Parameters
    ----------
    sub_df : pd.DataFrame
        Stripe Subscription DataFrame
    date : str
        A date of format 'YYYY/MM/DD'
    product : str or None, default None
        Name of a Stripe product
    interval : int, default 30
        Amount of days in the past to check

    Returns
    -------
    pd.DataFrame
        dataframe with subscription ids and their respective churn dates
    """
    df = sub_df.copy()
    if date is not None:
        date, last_date = _last_interval_days(date, interval)
        df = df[(df['canceled_at'] > last_date) &
                (df['canceled_at'] < date)]

    if product is not None:
        # enrich_subscriptions is needed
        df = df[df['name'] == product]

    subscriptions = df['id'].unique()

    churn_dates = []
    for subscription_id in subscriptions:
        subscription_df = df[df['id'] == subscription_id]
        churn_date = pd.NaT

        if ('active' not in subscription_df['status']) and ('past_due' not in subscription_df['status']):
            churn_date = subscription_df[subscription_df['status'] == 'canceled']['canceled_at'].max()

        churn_dates.append(churn_date)

    subscription_churn_dates = pd.DataFrame({'subscription_id': subscriptions, 'churn date': churn_dates})

    return subscription_churn_dates


def churned_customers(
        sub_df: pd.DataFrame,
        date: str,
        product: str or None = None,
        interval: int = 30
):
    """
    Get the subscribers that churned in the last interval (default 30) days from date ('YYYY/MM/DD').
    If product name is provided, filter subscriptions by product (Subscription must be enriched with product data).

    Parameters
    ----------
    sub_df : pd.DataFrame
        Stripe Subscription DataFrame
    date : str
        A date of format 'YYYY/MM/DD'
    product : str or None, default None
        Name of a Stripe product
    interval : int, default 30
        Amount of days in the past to check

    Returns
    -------
    pd.Series
        Pandas Series containing the ids of churned subscribers
    """
    # if product is not None, enrich_subscriptions is needed
    date, last_date = _last_interval_days(date, interval)

    customer_churn_dates = churn_dates(sub_df, date, product)
    last_month_churned_customers = pd.Series([], dtype=pd.StringDtype())
    if len(customer_churn_dates['churn date']) != 0:
        last_month_churned_customers = customer_churn_dates[(customer_churn_dates['churn date'] > last_date) &
                                                            (customer_churn_dates['churn date'] < date)]['customer']

    return last_month_churned_customers


def churned_subscriptions(
        sub_df: pd.DataFrame,
        date: str,
        product: str or None = None,
        interval: int = 30
):
    """
    Get the subscriptions that churned in the last interval (default 30) days from date ('YYYY/MM/DD').
    If product name is provided, filter subscriptions by product (Subscription must be enriched with product data).

    Parameters
    ----------
    sub_df : pd.DataFrame
        Stripe Subscription DataFrame
    date : str
        A date of format 'YYYY/MM/DD'
    product : str or None, default None
        Name of a Stripe product
    interval : int, default 30
        Amount of days in the past to check

    Returns
    -------
    pd.Series
        Pandas Series containing the ids of churned subscriptions
    """
    # if product is not None, enrich_subscriptions is needed
    date, last_date = _last_interval_days(date, interval)

    cur_active = active_subscriptions(sub_df, date, product)
    prev_active = active_subscriptions(sub_df, last_date, product)

    churned = list(set(prev_active) - set(cur_active))
    churned = pd.Series(churned, dtype=pd.StringDtype())

    return churned
