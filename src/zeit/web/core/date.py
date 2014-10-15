# -*- coding: utf-8 -*-
import datetime

import babel.dates
import zope.interface

import zeit.web.core.interfaces


# Will be made configurable with ZON-1038
limit = {'days': 3, 'hours': 8}
locale = 'de_DE'


def parse_date(date,
               date_format='%Y-%m-%dT%H:%M:%S.%f+00:00'):
    try:
        return datetime.datetime.strptime(date, date_format)
    except (TypeError, ValueError):
        return


@zope.interface.implementer(zeit.web.core.interfaces.IDeltaTimeEntity)
class DeltaTimeEntity(object):

    def __init__(self, delta):
        if not isinstance(delta, datetime.timedelta):
            raise TypeError
        self.delta = delta
        self.number = None
        self.text = None


@zope.interface.implementer(zeit.web.core.interfaces.IDeltaDaysEntity)
class DeltaDaysEntity(DeltaTimeEntity):

    def __init__(self, delta):
        super(DeltaDaysEntity, self).__init__(delta)
        self.number = self.delta.days
        date_text = babel.dates.format_timedelta(
            babel.dates.timedelta(days=self.delta.days), locale=locale)
        # Dirty hack, since babel does not understand
        # german cases (as in Kasus)
        self.text = date_text.replace('Tage', 'Tagen', 1)


@zope.interface.implementer(zeit.web.core.interfaces.IDeltaHoursEntity)
class DeltaHoursEntity(DeltaTimeEntity):

    def __init__(self, delta):
        # Since babel does round timedeltas inconveniently,
        # we need to perform some calculations manually.
        super(DeltaHoursEntity, self).__init__(delta)
        hours = self.delta.seconds / 3600
        self.number = hours
        self.text = babel.dates.format_timedelta(
            babel.dates.timedelta(hours=hours), locale=locale)


@zope.interface.implementer(zeit.web.core.interfaces.IDeltaMinutesEntity)
class DeltaMinutesEntity(DeltaTimeEntity):

    def __init__(self, delta):
        # Since babel does round timedeltas inconveniently,
        # we need to perform some calculations manually.
        super(DeltaMinutesEntity, self).__init__(delta)
        minutes = (self.delta.seconds % 3600) / 60
        self.number = minutes
        self.text = babel.dates.format_timedelta(
            babel.dates.timedelta(minutes=minutes), locale=locale)


@zope.interface.implementer(zeit.web.core.interfaces.IDeltaTime)
class DeltaTime(object):

    def __init__(self, date, base_date=None):
        if base_date is None:
            base_date = datetime.datetime.utcnow()
        self.date = date
        self.base_date = base_date
        self.delta = self.date - self.base_date

    def _get_babelfied_delta_time(self):
        self.days = zeit.web.core.date.DeltaDaysEntity(self.delta)
        self.hours = zeit.web.core.date.DeltaHoursEntity(self.delta)
        self.minutes = zeit.web.core.date.DeltaMinutesEntity(self.delta)

    def _filter_delta_time(self):
        if self.days.number >= limit['days']:
            self.hours = None
            self.minutes = None
        elif self.hours.number >= limit['hours']:
            self.minutes = None

    def _stringify_delta_time(self):
        return ' '.join(
            i.text for i in (self.days, self.hours, self.minutes)
            if i is not None and i.number != 0)

    def get_time_since_modification(self):
        self._get_babelfied_delta_time()
        self._filter_delta_time()
        stringified_dt = self._stringify_delta_time()
        return stringified_dt
