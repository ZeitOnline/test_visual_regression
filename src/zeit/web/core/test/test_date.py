# -*- coding: utf-8 -*-
import datetime

import pytest

import zeit.web.core.date


delta_time = zeit.web.core.date.DeltaTime(
    zeit.web.core.date.parse_date(
        '2014-10-07T14:42:00.1+00:00'),
    zeit.web.core.date.parse_date(
        '2014-10-09T19:22:00.1+00:00')
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


def test_parse_date_should_return_none_without_date():
    parsed_date = zeit.web.core.date.parse_date(None)
    assert parsed_date is None


def test_delta_time_should_store_delta_time():
    assert type(delta_time.delta) == datetime.timedelta
    assert delta_time.delta == datetime.timedelta(2, 16800)


def test_delta_days_entity_should_raise_type_error_on_invalid_param():
    with pytest.raises(TypeError):
        zeit.web.core.date.DeltaDaysEntity('timemachine')


def test_delta_days_entity_should_be_created():
    bde = zeit.web.core.date.DeltaDaysEntity(delta_time.delta)
    assert bde.number == 2
    assert bde.text == '2 Tage'


def test_delta_hours_entity_should_be_created():
    bhe = zeit.web.core.date.DeltaHoursEntity(delta_time.delta)
    assert bhe.number == 4
    assert bhe.text == '4 Stunden'


def test_delta_minutes_entity_should_be_created():
    bme = zeit.web.core.date.DeltaMinutesEntity(delta_time.delta)
    assert bme.number == 40
    assert bme.text == '40 Minuten'


def test_get_babelfied_delta_time_should_define_date_entities():
    delta_time._get_babelfied_delta_time()
    assert delta_time.hours.number == 4
    assert delta_time.minutes.text == '40 Minuten'


def test_filter_delta_time_should_modify_date_on_exceeding_hours_limit():
    limited_date = zeit.web.core.date.DeltaTime(
        zeit.web.core.date.parse_date(
            '2014-10-09T10:42:00.1+00:00'),
        zeit.web.core.date.parse_date(
            '2014-10-09T12:22:00.1+00:00')
    )
    limited_date._get_babelfied_delta_time()
    limited_date._filter_delta_time()
    assert limited_date.minutes is None
    assert limited_date.hours.number == 1
    assert limited_date.days.number == 0


def test_filter_delta_time_should_modify_date_on_exceeding_days_limit():
    limited_date = zeit.web.core.date.DeltaTime(
        zeit.web.core.date.parse_date(
            '2014-10-05T14:42:00.1+00:00'),
        zeit.web.core.date.parse_date(
            '2014-10-09T19:22:00.1+00:00')
    )
    limited_date._get_babelfied_delta_time()
    limited_date._filter_delta_time()
    assert limited_date.minutes is None
    assert limited_date.hours is None
    assert limited_date.days is None


def test_stringify_delta_time_should_return_string_representation_of_delta():
    delta_time._get_babelfied_delta_time()
    stringified_dt = delta_time._stringify_delta_time()
    assert stringified_dt == 'vor 2 Tagen 4 Stunden 40 Minuten'


def test_stringify_delta_time_should_ignore_values_of_zero():
    limited_date = zeit.web.core.date.DeltaTime(
        zeit.web.core.date.parse_date(
            '2014-10-08T18:42:00.1+00:00'),
        zeit.web.core.date.parse_date(
            '2014-10-09T19:22:00.1+00:00')
    )
    limited_date._get_babelfied_delta_time()
    stringified_dt = limited_date._stringify_delta_time()
    assert stringified_dt == 'vor 1 Tag 40 Minuten'


def test_get_time_since_modification_should_return_none_for_older_dates():
    stringified_dt = delta_time.get_time_since_modification()
    assert stringified_dt is None


def test_get_time_since_modification_should_return_delta_time_string():
    limited_date = zeit.web.core.date.DeltaTime(
        zeit.web.core.date.parse_date(
            '2014-10-09T14:42:00.1+00:00'),
        zeit.web.core.date.parse_date(
            '2014-10-09T17:22:00.1+00:00')
    )
    stringified_dt = limited_date.get_time_since_modification()
    assert stringified_dt == 'vor 2 Stunden'


def test_delta_time_should_default_to_now_for_base_date():
    dt = zeit.web.core.date.DeltaTime(
        zeit.web.core.date.parse_date(
            '2014-10-09T19:22:00.1+00:00'))
    dt._get_babelfied_delta_time()
    dt_until_now = dt._stringify_delta_time()
    assert dt_until_now is not None
    assert dt_until_now != ''
