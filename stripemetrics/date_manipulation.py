import pandas as pd
from datetime import datetime
import calendar


date_columns_names = {'billing_cycle_anchor', 'cancel_at', 'canceled_at', 'created', 'current_period_end',
                      'current_period_start', 'current_phase_start_date',
                      'current_phase_end_date', 'due_date', 'ended_at', 'requirements_current_deadline', 'start_date',
                      'timestamp', 'tos_acceptance_date', 'trial_start',
                      'trial_end', 'pause_collection_resumes_at', 'released_at', 'updated'}


# ------------ Time Manipulation -------------

def _max_hours(date_column):
    return date_column.replace(
        hour=datetime.max.hour,
        minute=datetime.max.minute,
        second=datetime.max.second,
        microsecond=datetime.max.microsecond
    )


def _min_hours(date_column):
    return date_column.replace(
        hour=datetime.min.hour,
        minute=datetime.min.minute,
        second=datetime.min.second,
        microsecond=datetime.min.microsecond
    )


# ------------ Date Manipulation -------------

def _rolling_month(date):
    cur_end = pd.Timestamp(date)
    cur_start = cur_end - pd.Timedelta(days=30)
    prev_end = cur_start
    prev_start = prev_end - pd.Timedelta(days=30)

    return cur_end, cur_start, prev_end, prev_start


def _last_interval_days(date, interval=30):
    date = pd.Timestamp(date)
    last_date = date - pd.Timedelta(days=interval)

    return date, last_date


def _up_to_month(date):
    # raises UserWarning when date.nanosecond != 0
    cur_end = pd.Timestamp(date)
    cur_start = cur_end.replace(nanosecond=0) - pd.offsets.MonthBegin()
    prev_end = cur_end.replace(nanosecond=0) - pd.DateOffset(months=1)
    prev_start = prev_end.replace(nanosecond=0) - pd.offsets.MonthBegin(1)

    return cur_end, cur_start, prev_end, prev_start


def _last_day_month(date):
    date = pd.Timestamp(date)
    last = calendar.monthrange(date.year, date.month)[1]

    return last


def _to_end_month(date):
    date = pd.Timestamp(date)
    last = _last_day_month(date)

    return last - date.day
