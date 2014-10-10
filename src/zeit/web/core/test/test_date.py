# -*- coding: utf-8 -*-
import datetime

import zeit.web.core.date


def test_parse_date_should_parse_iso_date():
    date = '2014-10-09T14:42:00.0+00:00'
    parsed_date = zeit.web.core.date.parse_date(date)
    assert type(parsed_date) == datetime.datetime
    assert parsed_date.isoformat() == '2014-10-09T14:42:00'


def test_parse_date_should_parse_date_with_custom_format():
    date = '09.10.2014 - 14:42'
    date_format = '%d.%m.%Y - %H:%M'
    parsed_date = zeit.web.core.date.parse_date(date, date_format)
    assert type(parsed_date) == datetime.datetime
    assert parsed_date.isoformat() == '2014-10-09T14:42:00'


def test_parse_date_should_return_none_on_invalid_date():
    date = 'timemachine'
    parsed_date = zeit.web.core.date.parse_date(date)
    assert parsed_date is None


def test_get_time_delta_should_return_time_delta():
    base_date = zeit.web.core.date.parse_date(
        '2014-10-09T14:42:00.1+00:00')
    date = zeit.web.core.date.parse_date(
        '2014-10-09T19:22:00.1+00:00')
    delta = zeit.web.core.date.get_time_delta(date, base_date)
    assert delta == {'hours': u'4 Stunden', 'minutes': u'40 Minuten'}


def test_get_time_delta_should_return_none_on_invalid_date():
    date = zeit.web.core.date.parse_date(
        'timemachine')
    delta = zeit.web.core.date.get_time_delta(date)
    assert delta is None
