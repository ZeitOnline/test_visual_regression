# -*- coding: utf-8 -*-
import datetime
import dateutil.parser

import babel.dates
import zope.interface

import zeit.web
import zeit.web.core.article
import zeit.web.core.interfaces
import zeit.web.core.template

locale = 'de_DE'


@zeit.web.register_filter
def parse_date(date,
               date_format='%Y-%m-%dT%H:%M:%S.%f+00:00'):
    try:
        if date_format == 'iso-8601':
            return dateutil.parser.parse(date)
        else:
            utc = babel.dates.get_timezone('UTC')
            dt = datetime.datetime.strptime(date, date_format)
            return dt.replace(tzinfo=utc)
    except (TypeError, ValueError, AttributeError):
        return


@zeit.web.register_filter
def mod_date(resource):
    try:
        pub_info = zeit.cms.workflow.interfaces.IPublishInfo(resource)
        # mimic zeit.web.core.view.date_last_published_semantic
        # whould be unnecessary if date_last_published_semantic is never before
        # first_released and initially undefined or equal first_released
        # but it's not like that [ms]
        modified = pub_info.date_last_published_semantic
        released = pub_info.date_first_released
        tz = babel.dates.get_timezone('Europe/Berlin')
        if zeit.web.core.article.ILiveblogArticle.providedBy(resource):
            liveblog = zeit.web.core.interfaces.ILiveblogInfo(resource)
            if liveblog.last_modified:
                if not modified or modified < liveblog.last_modified:
                    return liveblog.last_modified
        # use 60s of tolerance before displaying a modification date
        if (released and modified and
                modified - released > datetime.timedelta(seconds=60)):
            return modified.astimezone(tz)
        # fall back to date_last_published_semantic needed at least for
        # test files without date_first_released
        if released:
            return released.astimezone(tz)
        elif modified:
            return modified.astimezone(tz)
    except (TypeError, AttributeError):
        return


@zeit.web.register_filter
def release_date(resource):
    try:
        pub_info = zeit.cms.workflow.interfaces.IPublishInfo(resource)
        if pub_info.date_first_released:
            tz = babel.dates.get_timezone('Europe/Berlin')
            return pub_info.date_first_released.astimezone(tz)
        return pub_info.date_first_released
    except TypeError:
        return


@zeit.web.register_filter
def format_comment_date(comment_date, base_date=None):
    if not isinstance(comment_date, datetime.datetime):
        return ''
    interval = DeltaTime(comment_date, base_date)
    if interval.delta.days < 365:
        return interval.get_time_since_comment_posting()
    else:
        return zeit.web.core.template.format_date(comment_date, 'long')


@zeit.web.register_filter
def format_timedelta(date, absolute=False, format='short', **kwargs):
    if not isinstance(date, datetime.datetime):
        return ''
    interval = DeltaTime(date)
    relative = interval.get_time_since_modification(**kwargs)
    if absolute and not relative:
        return zeit.web.core.template.format_date(date, format)
    return relative or ''


@zeit.web.register_global
def get_delta_time_from_article(article, base_date=None):
    modification = mod_date(article)
    if not isinstance(modification, datetime.datetime):
        return None
    delta = DeltaTime(modification, base_date)
    delta = delta.get_time_since_modification()
    if delta:
        return delta.title()


@zope.interface.implementer(zeit.web.core.interfaces.IDeltaTimeEntity)
class DeltaTimeEntity(object):

    def __init__(self, delta):
        if not isinstance(delta, datetime.timedelta):
            raise TypeError()
        self.delta = delta
        self.number = None
        self.text = None


@zope.interface.implementer(zeit.web.core.interfaces.IDeltaDaysEntity)
class DeltaDaysEntity(DeltaTimeEntity):

    def __init__(self, delta):
        super(DeltaDaysEntity, self).__init__(delta)
        days = self.delta.days
        if (self.delta.days < 0):
            days = int(self.delta.days + float(self.delta.seconds) / 3600 / 24)
        self.number = days
        self.text = babel.dates.format_timedelta(
            babel.dates.timedelta(days=days),
            threshold=1, locale=locale)


@zope.interface.implementer(zeit.web.core.interfaces.IDeltaHoursEntity)
class DeltaHoursEntity(DeltaTimeEntity):

    def __init__(self, delta):
        # Since babel does round timedeltas inconveniently,
        # we need to perform some calculations manually.
        super(DeltaHoursEntity, self).__init__(delta)
        hours = self.delta.seconds / 3600
        if (self.delta.days < 0):
            hours = (3600 * 24 - self.delta.seconds) / 3600
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
        if (self.delta.days < 0):
            minutes = ((3600 * 24 - self.delta.seconds) % 3600) / 60
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
        if (self.delta.days < 0):
            seconds = (3600 * 24 - self.delta.seconds) % 60
        self.number = seconds
        self.text = babel.dates.format_timedelta(
            babel.dates.timedelta(seconds=seconds),
            threshold=1, locale=locale)


@zope.interface.implementer(zeit.web.core.interfaces.IDeltaTime)
class DeltaTime(object):

    def __init__(self, date, base_date=None):
        self.date = date
        self.base_date = base_date or datetime.datetime.now(date.tzinfo)
        self.delta = self.base_date - self.date
        # configuration for display
        self.limit = {
            'days': 1,  # blank any time data after this many days
            'hours': 1  # blank minutes data after this many hours
        }
        self.hide = {
            'hours': 3  # suppress delta after this many hours
        }

    def _get_babelfied_delta_time(self):
        self.days = zeit.web.core.date.DeltaDaysEntity(self.delta)
        self.hours = zeit.web.core.date.DeltaHoursEntity(self.delta)
        self.minutes = zeit.web.core.date.DeltaMinutesEntity(self.delta)
        self.seconds = zeit.web.core.date.DeltaSecondsEntity(self.delta)

    def _filter_delta_time(self):
        if (self.hide and abs(self.delta) >= datetime.timedelta(**self.hide)):
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
        prefix = 'vor '
        if self.delta.seconds + self.delta.days * 24 * 3600 < 0:
            prefix = 'in '
        # Dirty hack, since we are building the string ourself
        # instead of using babels "add_direction"
        return prefix + human_readable.replace('Tage', 'Tagen', 1).replace(
            'Monate', 'Monaten', 1).replace('Jahre', 'Jahren', 1)

    def get_time_since_modification(self, **kwargs):
        if len(kwargs):
            self.hide = kwargs
        self._get_babelfied_delta_time()
        self._filter_delta_time()
        stringified_dt = self._stringify_delta_time()
        return stringified_dt

    def get_time_since_comment_posting(self):
        self.hide = None
        return self.get_time_since_modification() or ''
