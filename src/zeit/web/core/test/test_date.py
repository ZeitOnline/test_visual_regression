# -*- coding: utf-8 -*-
import datetime

import pytest

import zeit.web.core.date


babel_date = zeit.web.core.date.BabelDate(
    zeit.web.core.date.parse_date(
        '2014-10-09T19:22:00.1+00:00'),
    zeit.web.core.date.parse_date(
        '2014-10-07T14:42:00.1+00:00')
)


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


def test_babel_date_should_store_delta_time():
    assert type(babel_date.delta) == datetime.timedelta
    assert babel_date.delta == datetime.timedelta(2, 16800)


def test_babel_days_entity_should_raise_type_error_on_invalid_param():
    with pytest.raises(TypeError):
        zeit.web.core.date.BabelDaysEntity('timemachine')


def test_babel_days_entity_should_be_created():
    bde = zeit.web.core.date.BabelDaysEntity(babel_date.delta)
    assert bde.number == 2
    assert bde.text == '2 Tagen'


def test_babel_hours_entity_should_be_created():
    bhe = zeit.web.core.date.BabelHoursEntity(babel_date.delta)
    assert bhe.number == 4
    assert bhe.text == '4 Stunden'


def test_babel_minutes_entity_should_be_created():
    bme = zeit.web.core.date.BabelMinutesEntity(babel_date.delta)
    assert bme.number == 40
    assert bme.text == '40 Minuten'


def test_get_babelfied_delta_time_should_define_date_entities():
    babel_date._get_babelfied_delta_time()
    assert babel_date.hours.number == 4
    assert babel_date.minutes.text == '40 Minuten'


def test_filter_delta_time_should_modify_date_on_exceeding_hours_limit():
    limited_date = zeit.web.core.date.BabelDate(
        zeit.web.core.date.parse_date(
            '2014-10-09T19:22:00.1+00:00'),
        zeit.web.core.date.parse_date(
            '2014-10-09T10:42:00.1+00:00')
    )
    limited_date._get_babelfied_delta_time()
    limited_date._filter_delta_time()
    assert limited_date.minutes is None
    assert limited_date.hours.number == 8
    assert limited_date.days.number == 0


def test_filter_delta_time_should_modify_date_on_exceeding_days_limit():
    limited_date = zeit.web.core.date.BabelDate(
        zeit.web.core.date.parse_date(
            '2014-10-09T19:22:00.1+00:00'),
        zeit.web.core.date.parse_date(
            '2014-10-05T14:42:00.1+00:00')
    )
    limited_date._get_babelfied_delta_time()
    limited_date._filter_delta_time()
    assert limited_date.minutes is None
    assert limited_date.hours is None
    assert limited_date.days.number == 4


def test_stringify_delta_time_should_return_string_representation_of_delta():
    babel_date._get_babelfied_delta_time()
    stringified_dt = babel_date._stringify_delta_time()
    assert stringified_dt == '2 Tagen 4 Stunden 40 Minuten'


def test_get_time_since_modification_should_return_delta_time_string():
    stringified_dt = babel_date.get_time_since_modification()
    assert stringified_dt == '2 Tagen 4 Stunden 40 Minuten'
