# -*- coding: utf-8 -*-
import datetime

import babel.dates


locale = 'de_DE'


def _babelfy_days_from_timedelta(delta):
    try:
        return (babel.dates.format_timedelta(
            babel.dates.timedelta(days=delta.days), locale=locale))
    except AttributeError:
        return


def _babelfy_hours_from_timedelta(delta):
    try:
        hours = delta.seconds / 3600
        return (babel.dates.format_timedelta(
            babel.dates.timedelta(hours=hours), locale=locale))
    except AttributeError:
        return


def _babelfy_minutes_from_timedelta(delta):
    try:
        minutes = (delta.seconds % 3600) / 60
        return (babel.dates.format_timedelta(
            babel.dates.timedelta(minutes=minutes), locale=locale))
    except AttributeError:
        return


def parse_date(date,
               date_format='%Y-%m-%dT%H:%M:%S.%f+00:00'):
    try:
        return datetime.datetime.strptime(date, date_format)
    except ValueError:
        return


def get_time_delta(date, base_date=datetime.datetime.utcnow()):
    # Since babel does round timedeltas inconveniently,
    # we need to perform some calculations manually.
    try:
        delta = date - base_date
        babel_delta = {
            'days': _babelfy_days_from_timedelta(delta),
            'hours': _babelfy_hours_from_timedelta(delta),
            'minutes': _babelfy_minutes_from_timedelta(delta),
        }
        return babel_delta
    except TypeError:
        return
