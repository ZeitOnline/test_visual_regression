import pytest
import requests
import urllib2

import zeit.web.core.date


def test_json_delta_time_from_date_should_return_delta_time(testserver,
                                                            testbrowser):
    browser = testbrowser(
        '{}/json/delta_time?'
        'date=2014-10-14T09%3A06%3A45.950590%2B00%3A00'
        '&base_date=2014-10-15T10%3A06%3A45.950590%2B00%3A00'.format(
            testserver.url))
    assert browser.contents == (
        '{"delta_time": {"time": "vor 1 Tag 1 Stunde"}}')


def test_json_delta_time_from_date_should_fallback_to_now_for_base_date(
        testserver, testbrowser):
    browser = testbrowser(
        '{}/json/delta_time?'
        'date=2014-10-15T10%3A06%3A45.950590%2B00%3A00'.format(
            testserver.url))
    assert browser.contents is not None
    assert browser.contents != ''


def test_json_delta_time_from_date_should_return_http_error_on_missing_params(
        testserver, testbrowser):
    with pytest.raises(urllib2.HTTPError):
        testbrowser('{}/json/delta_time'.format(testserver.url))


def test_json_delta_time_from_unique_id_should_return_delta_time(testserver,
                                                                 testbrowser,
                                                                 monkeypatch):
    now = zeit.web.core.date.parse_date('2014-10-17T16:53:59.780412+00:00')
    monkeypatch.setattr(zeit.web.core.date, 'utcnow', lambda: now)

    browser = testbrowser(
        '{}/json/delta_time?'
        'unique_id=http://xml.zeit.de/zeit-online/main-teaser-setup'.format(
            testserver.url))
    assert browser.contents == (
        '{"delta_time": ['
        '{"http://xml.zeit.de/zeit-online/cp-content/article-01": '
        '{"time": "vor 2 Tagen 2 Stunden"}}, '
        '{"http://xml.zeit.de/zeit-online/cp-content/article-02": '
        '{"time": "vor 2 Tagen 2 Stunden"}}]}')


def test_json_delta_time_from_unique_id_should_return_http_error_on_false_uid(
        testserver, testbrowser):
    with pytest.raises(urllib2.HTTPError):
        testbrowser('{}/json/delta_time?unique_id=foo'.format(testserver.url))


def test_json_delta_time_from_unique_id_should_return_http_error_on_article(
        testserver, testbrowser):
    with pytest.raises(urllib2.HTTPError):
        testbrowser('{}/json/delta_time?unique_id='
                    'http://xml.zeit.de/artikel/01'.format(testserver.url))


def test_json_delta_time_from_unique_id_should_use_custom_base_time(
        testserver, testbrowser):
    browser = testbrowser(
        '{}/json/delta_time?base_date=2014-10-16T09%3A06%3A45.95%2B00%3A00&'
        'unique_id=http://xml.zeit.de/zeit-online/main-teaser-setup'.format(
            testserver.url))
    assert 'vor 18 Stunden' in browser.contents


def test_http_header_should_contain_c1_header_fields(testserver, testbrowser):
    c1_track_doc_type = requests.head(
        testserver.url + "/zeit-magazin/index").headers['c1-track-doc-type']
    c1_track_channel = requests.head(
        testserver.url + "/zeit-magazin/index").headers['c1-track-channel']
    c1_track_kicker = requests.head(
        testserver.url + "/artikel/03").headers['c1-track-kicker']
    assert c1_track_doc_type == 'Centerpage'
    assert c1_track_channel == 'Lebensart'
    assert c1_track_kicker == 'Kolumne Die Ausleser'


def test_http_header_should_not_contain_empty_fields(
        testserver, testbrowser):
    with pytest.raises(KeyError):
        requests.head(
            testserver.url +
            "/zeit-magazin/index").headers['c1-track-sub-channel']
