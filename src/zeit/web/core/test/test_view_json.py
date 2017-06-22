import json
import urllib2

import pytest

import zeit.cms.interfaces
import zeit.cms.checkout.helper

import zeit.web.core.view_json


def test_centerpage_should_return_jsonp_with_timestamp_if_released(
        testbrowser):
    # published page returns its pubdate
    browser = testbrowser(
        '/json/update-time/zeit-online/main-teaser-setup?callback=foo123')
    pubstring = (
        '/**/foo123({\n  "last_published_semantic": '
        '"2014-11-18T12:18:27.293179+00:00", '
        '\n  "last_published": "2014-11-18T12:18:27.293179+00:00"\n});')
    assert browser.headers.type == 'application/javascript'
    assert pubstring == browser.contents


def test_centerpage_should_return_jsonp_with_timestamp_if_not_released(
        testbrowser):
    # published page returns empty string
    browser = testbrowser(
        '/json/update-time/zeit-online/teaser-serie-setup?callback=foo123')
    pubstring = (
        '/**/foo123({\n  "last_published_semantic": null, '
        '\n  "last_published": null\n});')
    assert browser.headers.type == 'application/javascript'
    assert pubstring == browser.contents


def test_json_update_time_handler_should_set_exipration_header(testbrowser):
    browser = testbrowser(
        '/json/update-time/zeit-online/main-teaser-setup')
    assert browser.headers.get('cache-control') == 'max-age=5'


def test_hp_topics_should_be_rendered(application, dummy_request):
    config = zeit.web.core.view_json.json_topic_config(dummy_request)

    assert config['topics'][0]['topic'] == 'Islamischer Staat'
    assert config['topics'][0]['url'] == ('http://www.zeit.de/schlagworte/'
                                          'organisationen/islamischer-staat/'
                                          'index')
    assert config['topics'][1]['topic'] == 'Bundeswehr'
    assert config['topics'][1]['url'] == ('http://www.zeit.de/schlagworte/'
                                          'themen/bundeswehr/index')
    assert config['topics'][2]['topic'] == 'Hongkong'
    assert config['topics'][2]['url'] == ('http://www.zeit.de/schlagworte/'
                                          'orte/hongkong/index')


def test_hp_topics_should_only_be_rendered_as_needed(application,
                                                     dummy_request,
                                                     workingcopy):
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/index')
    with zeit.cms.checkout.helper.checked_out(cp) as co:
        co.topiclink_url_3 = ''
        co.topiclink_label_3 = ''
    config = zeit.web.core.view_json.json_topic_config(
        dummy_request)
    assert len(config['topics']) == 2


def test_json_delta_time_from_date_should_return_none(testbrowser):
    browser = testbrowser(
        '/json/delta-time?'
        'date=2014-10-14T09%3A06%3A45.950590%2B00%3A00'
        '&base_date=2014-10-15T10%3A06%3A45.950590%2B00%3A00')
    assert browser.json == {"delta_time": {"time": None}}


def test_json_delta_time_from_date_should_return_delta_time(testbrowser):
    browser = testbrowser(
        '/json/delta-time?'
        'date=2014-10-14T09%3A06%3A45.950590%2B00%3A00'
        '&base_date=2014-10-14T10%3A36%3A45.950590%2B00%3A00')
    assert browser.json == {"delta_time": {"time": "vor 1 Stunde"}}


def test_json_delta_time_from_date_should_fallback_to_now_for_base_date(
        testbrowser):
    browser = testbrowser(
        '/json/delta-time?'
        'date=2014-10-15T10%3A06%3A45.950590%2B00%3A00')
    assert browser.contents is not None
    assert browser.contents != ''


def test_json_delta_time_from_date_should_return_http_error_on_missing_params(
        testbrowser):
    with pytest.raises(urllib2.HTTPError):
        testbrowser('/json/delta-time')


def test_json_delta_time_from_unique_id_should_return_delta_time(
        testbrowser, clock):
    clock.freeze(zeit.web.core.date.parse_date(
        '2014-10-15T16:23:59.780412+00:00'))

    browser = testbrowser(
        '/json/delta-time?'
        'unique_id=http://xml.zeit.de/zeit-online/main-teaser-setup')
    content = json.loads(browser.contents)
    a1 = 'http://xml.zeit.de/zeit-online/cp-content/article-01'
    a2 = 'http://xml.zeit.de/zeit-online/cp-content/article-02'
    assert content['delta_time'][a1] == 'Vor 1 Stunde'
    assert content['delta_time'][a2] == 'Vor 30 Minuten'


def test_json_delta_time_from_unique_id_should_return_http_error_on_false_uid(
        testbrowser):
    with pytest.raises(urllib2.HTTPError):
        testbrowser('/json/delta-time?unique_id=foo')


def test_json_delta_time_from_unique_id_should_return_http_error_on_article(
        testbrowser):
    with pytest.raises(urllib2.HTTPError) as error:
        testbrowser('/json/delta-time?unique_id='
                    'http://xml.zeit.de/zeit-magazin/article/01')
    assert error.value.getcode() == 400


def test_json_delta_time_from_unique_id_should_use_custom_base_time(
        testbrowser):
    browser = testbrowser(
        '/json/delta-time?base_date=2014-10-15T16%3A06%3A45.95%2B00%3A00&'
        'unique_id=http://xml.zeit.de/zeit-online/main-teaser-setup')
    content = json.loads(browser.contents)
    a1 = 'http://xml.zeit.de/zeit-online/cp-content/article-01'
    a2 = 'http://xml.zeit.de/zeit-online/cp-content/article-02'
    assert content['delta_time'][a1] == 'Vor 1 Stunde'
    assert content['delta_time'][a2] == 'Vor 12 Minuten'
