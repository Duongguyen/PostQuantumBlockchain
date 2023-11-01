from datetime import datetime

import pytz


def aware_to_naive(dt):
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(pytz.utc).replace(tzinfo=None)


def naive_to_aware(dt, tz=pytz.utc):
    if dt.tzinfo is not None:
        return dt.astimezone(pytz.utc).astimezone(tz)
    return pytz.utc.localize(dt).astimezone(tz)


def naive_now():
    return aware_to_naive(aware_now())


def aware_now():
    return datetime.now(tz=pytz.utc)