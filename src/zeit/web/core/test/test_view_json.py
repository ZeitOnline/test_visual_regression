import json
import urllib2

import mock
import pytest
import requests
import zope.component

import zeit.cms.interfaces
import zeit.cms.checkout.helper

import zeit.web.core.navigation
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


def test_json_ressort_list_should_produce_list_of_ressorts(testbrowser):
    browser = testbrowser('/json/ressort-list')
    assert len(browser.json)
    assert browser.json[0] == {
        'name': 'Politik',
        'uniqueId': 'http://xml.zeit.de/politik/index'}


def test_json_ressort_list_should_exclude_advertorials(
        monkeypatch, testbrowser):
    def navigation():
        return [
            zeit.web.core.navigation.NavigationItem(
                'Ad.0.0.0/adv', 'ad', 'http://zeit.to/advertorial', 'Anzeige'),
            zeit.web.core.navigation.NavigationItem(
                'Politik.0.1/pol', 'Politik', 'http://zeit.to/politik')]
    monkeypatch.setattr(zeit.web.core.navigation.NAVIGATION_SOURCE.navigation,
                        'values', navigation)
    browser = testbrowser('/json/ressort-list')
    assert len(browser.json) == 1


@pytest.mark.parametrize('json', [None, {'uniqueIds': 2}, {'uniqueIds': []}])
def test_json_article_query_should_do_sanity_checks_on_post(json, testserver):
    resp = requests.post('%s/json/article-query' % testserver.url, json=json)
    assert resp.status_code == 400


def test_json_article_query_should_respond_to_good_request(testserver):
    json = {'uniqueIds': ['http://xml.zeit.de/zeit-online/article/zeit']}
    resp = requests.post('%s/json/article-query' % testserver.url, json=json)
    assert resp.ok


def test_json_article_query_should_construct_correct_solr_queries(
        application, monkeypatch):
    request = mock.MagicMock()
    request.json_body = {'uniqueIds': ['foo://1', 'bar://2']}
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    search = mock.MagicMock(return_value=[])
    monkeypatch.setattr(solr, 'search', search)
    zeit.web.core.view_json.json_article_query(request)
    args, kw = search.call_args
    assert args[0] == '(uniqueId:"foo://1" OR uniqueId:"bar://2")'
    assert kw['fq'] == 'type:(article)'


def test_json_article_query_should_transform_solr_fields(application):
    request = mock.Mock()
    request.route_url = mock.MagicMock(return_value='//zeit.to/')
    request.json_body = {'uniqueIds': [
        'http://xml.zeit.de/zeit-online/cp-content/article-01']}
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{
        'date_first_released': '2017-05-03T15:01:26.098814+00:00',
        'date_last_published': '2017-05-03T15:01:26.098814+00:00',
        'keywords': ['kw-1', 'kw-3', 'kw-8'],
        'ressort': 'my-ressort',
        'sub_ressort': 'my-sub-ressort',
        'supertitle': 'my-super-title',
        'teaser_text': 'my-teaser-text',
        'title': 'my-title',
        'uniqueId': 'http://xml.zeit.de/zeit-online/cp-content/article-01',
        'uuid': 'my-uuid'
    }]
    response = zeit.web.core.view_json.json_article_query(request)
    assert response == [{
        'date_first_released': '2017-05-03T15:01:26.098814+00:00',
        'date_last_published': '2017-05-03T15:01:26.098814+00:00',
        'keywords': ['kw-1', 'kw-3', 'kw-8'],
        'lead_article': True,
        'ressort': 'my-ressort',
        'sub_ressort': 'my-sub-ressort',
        'supertitle': 'my-super-title',
        'teaser_text': 'my-teaser-text',
        'title': 'my-title',
        'uniqueId': 'http://xml.zeit.de/zeit-online/cp-content/article-01',
        'url': '//zeit.to/zeit-online/cp-content/article-01',
        'uuid': 'my-uuid'
    }]
