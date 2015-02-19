# -*- coding: utf-8 -*-
import datetime

import babel.dates
import zope.interface

import zeit.web
import zeit.web.core.interfaces


# Will be made configurable with ZON-1038
limit = {'days': 1, 'hours': 1}
hide = {'days': 0, 'hours': 3}
locale = 'de_DE'


def utcnow():
    # XXX Wrapper function needed on module level, because we need to patch
    #     it in tests.
    return datetime.datetime.utcnow()


def parse_date(date,
               date_format='%Y-%m-%dT%H:%M:%S.%f+00:00'):
    try:
        return datetime.datetime.strptime(date, date_format)
    except (TypeError, ValueError):
        return


@zeit.web.register_filter
def mod_date(resource):
    try:
        pub_info = zeit.cms.workflow.interfaces.IPublishInfo(resource)
        return (pub_info.date_last_published_semantic or
                pub_info.date_last_published)
    except TypeError:
        return


@zeit.web.register_global
def get_delta_time(article, base_date=None):
    modification = mod_date(article)
    if modification is not None:
        dt = DeltaTime(modification.replace(tzinfo=None), base_date)
        return dt.get_time_since_modification()


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
        self.text = babel.dates.format_timedelta(
            babel.dates.timedelta(days=self.delta.days),
            threshold=1, locale=locale)


@zope.interface.implementer(zeit.web.core.interfaces.IDeltaHoursEntity)
class DeltaHoursEntity(DeltaTimeEntity):

    def __init__(self, delta):
        # Since babel does round timedeltas inconveniently,
        # we need to perform some calculations manually.
        super(DeltaHoursEntity, self).__init__(delta)
        hours = self.delta.seconds / 3600
        self.number = hours
        self.text = babel.dates.format_timedelta(
            babel.dates.timedelta(hours=hours),
            threshold=1, locale=locale)


@zope.interface.implementer(zeit.web.core.interfaces.IDeltaMinutesEntity)
class DeltaMinutesEntity(DeltaTimeEntity):

    def __init__(self, delta):
        # Since babel does round timedeltas inconveniently,
        # we need to perform some calculations manually.
        super(DeltaMinutesEntity, self).__init__(delta)
        minutes = (self.delta.seconds % 3600) / 60
        self.number = minutes
        self.text = babel.dates.format_timedelta(
            babel.dates.timedelta(minutes=minutes),
            threshold=1, locale=locale)


@zope.interface.implementer(zeit.web.core.interfaces.IDeltaTime)
class DeltaTime(object):

    def __init__(self, date, base_date=None):
        self.date = date
        self.base_date = base_date or utcnow()
        self.delta = self.base_date - self.date

    def _get_babelfied_delta_time(self):
        self.days = zeit.web.core.date.DeltaDaysEntity(self.delta)
        self.hours = zeit.web.core.date.DeltaHoursEntity(self.delta)
        self.minutes = zeit.web.core.date.DeltaMinutesEntity(self.delta)

    def _filter_delta_time(self):
        if (self.days.number >= hide['days'] and self.hours.number +
                self.days.number * 24 >= hide['hours']):
            self.days = None
            self.hours = None
            self.minutes = None
        elif self.days.number >= limit['days']:
            self.hours = None
            self.minutes = None
        elif self.hours.number + self.days.number * 24 >= limit['hours']:
            self.minutes = None

    def _stringify_delta_time(self):
        human_readable = ' '.join(
            i.text for i in (self.days, self.hours, self.minutes)
            if i is not None and i.number != 0)
        if human_readable is '':
            return
        # Dirty hack, since babel does not understand
        # german cases (as in Kasus)
        return 'vor ' + human_readable.replace(
            'Tage', 'Tagen', 1).replace(
            'Monate', 'Monaten', 1)

    def get_time_since_modification(self):
        self._get_babelfied_delta_time()
        self._filter_delta_time()
        stringified_dt = self._stringify_delta_time()
        return stringified_dt
