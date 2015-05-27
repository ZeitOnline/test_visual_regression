# -*- coding: utf-8 -*-
import datetime

import babel.dates
import zope.interface

import zeit.web
import zeit.web.core.interfaces

locale = 'de_DE'


def get_base_date(date):
    # XXX Wrapper function needed on module level, because we need to patch
    #     it in tests.
    return datetime.datetime.now(date.tzinfo)


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


@zeit.web.register_filter
def format_comment_date(comment_date, base_date=None):
    interval = DeltaTime(comment_date, base_date)
    if interval.delta.days < 365:
        return interval.get_time_since_comment_posting()
    else:
        return babel.dates.format_datetime(
            comment_date, "d. MMMM yyyy, H:mm 'Uhr'", locale=locale)


@zeit.web.register_global
def get_delta_time_from_article(article, base_date=None):
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


@zope.interface.implementer(zeit.web.core.interfaces.IDeltaSecondsEntity)
class DeltaSecondsEntity(DeltaTimeEntity):

    def __init__(self, delta):
        # Since babel does round timedeltas inconveniently,
        # we need to perform some calculations manually.
        super(DeltaSecondsEntity, self).__init__(delta)
        seconds = self.delta.seconds % 60
        self.number = seconds
        self.text = babel.dates.format_timedelta(
            babel.dates.timedelta(seconds=seconds),
            threshold=1, locale=locale)


@zope.interface.implementer(zeit.web.core.interfaces.IDeltaTime)
class DeltaTime(object):

    def __init__(self, date, base_date=None):
        self.date = date
        self.base_date = base_date or get_base_date(date)
        self.delta = self.base_date - self.date
        # configuration for display
        self.limit = {
            'days': 1,  # blank any time data after this many days
            'hours': 1  # blank minutes data after this many hours
        }
        self.hide = {
            'days': 0,  # suppress delta after this many days
            'hours': 3  # suppress delta after this many hours
        }

    def _get_babelfied_delta_time(self):
        self.days = zeit.web.core.date.DeltaDaysEntity(self.delta)
        self.hours = zeit.web.core.date.DeltaHoursEntity(self.delta)
        self.minutes = zeit.web.core.date.DeltaMinutesEntity(self.delta)
        self.seconds = zeit.web.core.date.DeltaSecondsEntity(self.delta)

    def _filter_delta_time(self):
        if (self.hide and (
                (self.hide.get('days') and
                 self.days.number >= self.hide['days']) or
                (self.hide.get('hours') and self.hours.number +
                 self.days.number * 24 >= self.hide['hours']))):
            self.days = None
            self.hours = None
            self.minutes = None
            self.seconds = None
        elif self.days.number >= self.limit['days']:
            self.hours = None
            self.minutes = None
            self.seconds = None
        elif self.hours.number + self.days.number * 24 >= self.limit['hours']:
            self.minutes = None
            self.seconds = None
        elif self.delta.days or self.delta.seconds > 59:
            self.seconds = None

    def _stringify_delta_time(self):
        human_readable = ' '.join(
            i.text for i in (self.days, self.hours, self.minutes, self.seconds)
            if i is not None and i.number != 0)
        if human_readable is '':
            return
        # Dirty hack, since we are building the string ourself
        # instead of using babels "add_direction"
        return 'vor ' + human_readable.replace(
            'Tage', 'Tagen', 1).replace(
            'Monate', 'Monaten', 1).replace(
            'Jahre', 'Jahren', 1)

    def get_time_since_modification(self):
        self._get_babelfied_delta_time()
        self._filter_delta_time()
        stringified_dt = self._stringify_delta_time()
        return stringified_dt

    def get_time_since_comment_posting(self):
        self.hide = None
        return self.get_time_since_modification() or ''
