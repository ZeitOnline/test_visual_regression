# -*- coding: utf-8 -*-
import datetime

import babel.dates


locale = 'de_DE'


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
        hours = delta.seconds / 3600
        minutes = (delta.seconds % 3600) / 60
        babel_hours = (
            babel.dates.format_timedelta(
                babel.dates.timedelta(hours=hours), locale=locale))
        babel_minutes = (
            babel.dates.format_timedelta(
                babel.dates.timedelta(minutes=minutes), locale=locale))
        babel_delta = {'hours': babel_hours, 'minutes': babel_minutes}
        return babel_delta
    except TypeError:
        return
