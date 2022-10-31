import pandas as pd
import numpy as np
from stripemetrics.data_transform import active_subscribers, active_subscriptions, \
    churned_customers, churned_subscriptions, enrich_subscriptions, new_subscribers, new_subscriptions


def total_mrr(sub_df, date, product=None):
    # enrich_subscriptions is needed
    # note: enrich_subscriptions here does not need prod_df
    active_subs = active_subscriptions(sub_df, date, product)
    df = sub_df[sub_df['id'].isin(active_subs)].copy()
    df = enrich_subscriptions(df)

    if product:
        df = df[df['name'] == product]

    # discounts only affect MRR when coupon_duration is forever
    df['percent_off'] = np.where(df['coupon_duration'] == 'forever', df['percent_off'], 0)

    # creating a column for monthly normalized amount with discounts applied
    df['plan_amount_month'] = np.where(
        df['plan_interval'] == 'month', (1 / 100) * df['plan_amount'] * df['quantity'] * (1 - df['percent_off'] / 100),
        np.where(
            df['plan_interval'] == 'year',
            (1 / 100) * (1 / 12) * df['plan_amount'] * df['quantity'] * (1 - df['percent_off'] / 100), np.nan))

    mrr = df['plan_amount_month'].sum()

    return mrr


def revenue_per_subscriber(sub_df, date, product=None):
    # enrich_subscriptions is needed
    revenue = 0
    active = active_subscribers(sub_df, date, product).shape[0]
    if active != 0:
        revenue = total_mrr(sub_df, date, product) / active

    return revenue


def mrr_per_customer(customer_id, sub_df, date, product=None, interval=14):
    # enrich_subscriptions is needed
    # note: enrich_subscriptions here does not need prod_df
    date = pd.Timestamp(date)

    # filtering only the subscriptions related to the customer
    subscriber_df = sub_df[sub_df['customer'] == customer_id].copy()

    # filtering the active subscriptions
    active_subscriber_df = active_subscriptions(subscriber_df, date, product, interval)

    customer_mrr = total_mrr(subscriber_df, date, product)

    return customer_mrr


def churned_subscribers_rate(sub_df, date, product=None, interval=30):
    # if product is not None, enrich_subscriptions is needed
    date_ = pd.Timestamp(date)
    prev_date = date_ - pd.Timedelta(days=interval)

    churned = churned_customers(sub_df, date_, product)
    prev_active = active_subscribers(sub_df, prev_date)
    new = new_subscribers(sub_df, date_, product)

    churn_rate = 0

    if (len(prev_active) + len(new)) != 0:
        churn_rate = len(churned) / (len(prev_active) + len(new))

    return churn_rate


def subscribers_retention_rate(sub_df, date, product=None, interval=30):
    # if product is not None, enrich_subscriptions is needed
    date_ = pd.Timestamp(date)
    prev_date = date_ - pd.Timedelta(days=interval)

    cur_active = active_subscribers(sub_df, date_, product)
    prev_active = active_subscribers(sub_df, prev_date, product)
    new = new_subscribers(sub_df, date_, product)

    retention_rate = 0

    if len(prev_active) != 0:
        retention_rate = (len(cur_active) - len(new)) / len(prev_active)

    return retention_rate


def churned_subscriptions_rate(sub_df, date, product=None, interval=30):
    # if product is not None, enrich_subscriptions is needed
    date_ = pd.Timestamp(date)
    prev_date = date_ - pd.Timedelta(days=interval)

    churned = churned_subscriptions(sub_df, date_, product)
    prev_active = active_subscriptions(sub_df, prev_date, product)
    new = new_subscriptions(sub_df, date_, product)

    churn_rate = 0

    if (len(prev_active) + len(new)) != 0:
        churn_rate = len(churned) / (len(prev_active) + len(new))

    return churn_rate


def subscription_retention_rate(sub_df, date, product=None, interval=30):
    # if product is not None, enrich_subscriptions is needed
    date_ = pd.Timestamp(date)
    prev_date = date_ - pd.Timedelta(days=interval)

    cur_active = active_subscriptions(sub_df, date_, product)
    prev_active = active_subscriptions(sub_df, prev_date, product)
    new = new_subscriptions(sub_df, date_, product)

    retention_rate = 0

    if len(prev_active) != 0:
        retention_rate = (len(cur_active) - len(new)) / len(prev_active)

    return retention_rate
