import numpy as np
from stripemetrics.date_manipulation import _last_interval_days, _max_hours


def total_revenue(ch_df, date, product=None, prod_df=None, interval=_last_interval_days):
    # enrich_charges needed
    charges = ch_df.copy()
    date_, last_date = interval(date)

    # this does not warn anything if user passes product and not prod_df, should change it
    if (product is not None) and (prod_df is not None):
        charges['product_key'] = charges.apply(
            lambda x: x['metadata']['product_key'] if 'product_key' in x['metadata'].keys() is not None else np.nan,
            axis=1)

        product_id = prod_df[prod_df['name'] == product]['id'].values[0]
        charges = charges[charges['product_key'] == product_id]

    revenue = charges[(charges['created'] >= last_date) &
                      (charges['created'] <= _max_hours(date_)) &
                      (charges['refunded'] == False)]['amount_captured_usd'].sum()

    return revenue


def total_refunded(ch_df, date, product=None, interval=_last_interval_days):
    charges = ch_df.copy()
    date_, last_date = interval(date)

    if product is not None:
        # enrich_charges needed
        charges = charges[charges['name'] == product]

    charges['amount_refunded'] = charges['amount_refunded'] / 100
    refunded = charges[(charges['created'] >= last_date) &
                       (charges['created'] <= _max_hours(date_))]['amount_refunded'].sum()

    return refunded


def total_refunds(ch_df, date, product=None, interval=_last_interval_days):
    charges = ch_df.copy()
    date_, last_date = interval(date)

    if product is not None:
        # enrich_charges needed
        charges = charges[charges['name'] == product]

    refunded = charges[(charges['created'] >= last_date) &
                       (charges['created'] <= _max_hours(date_))]['refunded'].sum()

    return refunded
