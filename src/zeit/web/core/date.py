# -*- coding: utf-8 -*-
import datetime

import babel.dates
import grokcore.component

import zeit.web.core.interfaces


# Will be made configurable with ZON-1038
limit = {'days': 3, 'hours': 8}
locale = 'de_DE'


def parse_date(date,
               date_format='%Y-%m-%dT%H:%M:%S.%f+00:00'):
    try:
        return datetime.datetime.strptime(date, date_format)
    except ValueError:
        return


@grokcore.component.implementer(zeit.web.core.interfaces.IBabelDateEntity)
class BabelDateEntity(object):

    def __init__(self, delta):
        if not isinstance(delta, datetime.timedelta):
            raise TypeError
        self.delta = delta


@grokcore.component.implementer(zeit.web.core.interfaces.IBabelDaysEntity)
class BabelDaysEntity(BabelDateEntity):

    def __init__(self, delta):
        super(BabelDaysEntity, self).__init__(delta)
        self.number = self.delta.days
        date_text = babel.dates.format_timedelta(
            babel.dates.timedelta(days=self.delta.days), locale=locale)
        # Dirty hack, since babel does not understand
        # german cases (as in Kasus)
        self.text = date_text.replace('Tage', 'Tagen', 1)


@grokcore.component.implementer(zeit.web.core.interfaces.IBabelHoursEntity)
class BabelHoursEntity(BabelDateEntity):

    def __init__(self, delta):
        # Since babel does round timedeltas inconveniently,
        # we need to perform some calculations manually.
        super(BabelHoursEntity, self).__init__(delta)
        hours = self.delta.seconds / 3600
        self.number = hours
        self.text = babel.dates.format_timedelta(
            babel.dates.timedelta(hours=hours), locale=locale)


@grokcore.component.implementer(zeit.web.core.interfaces.IBabelMinutesEntity)
class BabelMinutesEntity(BabelDateEntity):

    def __init__(self, delta):
        # Since babel does round timedeltas inconveniently,
        # we need to perform some calculations manually.
        super(BabelMinutesEntity, self).__init__(delta)
        minutes = (self.delta.seconds % 3600) / 60
        self.number = minutes
        self.text = babel.dates.format_timedelta(
            babel.dates.timedelta(minutes=minutes), locale=locale)


@grokcore.component.implementer(zeit.web.core.interfaces.IBabelDate)
class BabelDate(object):

    def __init__(self, date, base_date=datetime.datetime.utcnow()):
        self.date = date
        self.base_date = base_date
        self.delta = self.date - self.base_date

    def _get_babelfied_delta_time(self):
        self.days = zeit.web.core.date.BabelDaysEntity(self.delta)
        self.hours = zeit.web.core.date.BabelHoursEntity(self.delta)
        self.minutes = zeit.web.core.date.BabelMinutesEntity(self.delta)

    def _filter_delta_time(self):
        if self.days.number >= limit['days']:
            self.hours = None
            self.minutes = None
        elif self.hours.number >= limit['hours']:
            self.minutes = None

    def _stringify_delta_time(self):
        return ' '.join(
            i.text for i in (self.days, self.hours, self.minutes)
            if i is not None)

    def get_time_since_modification(self):
        self._get_babelfied_delta_time()
        self._filter_delta_time()
        stringified_dt = self._stringify_delta_time()
        return stringified_dt
