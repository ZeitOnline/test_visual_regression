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


@pytest.mark.parametrize('json', [
    ['uniqueId'],
    {'uniqueIds': 2},
    {'uniqueIds': ['clearly_not_a_unique_id']},
    {'uuids': [False]},
    {'uuids': ['clearly-not-a-uuid']}])
def test_json_article_query_should_do_sanity_checks_on_post(json, testserver):
    resp = requests.post('%s/json/article-query' % testserver.url, json=json)
    assert resp.status_code == 400


def test_json_article_query_should_return_empty_for_empty_query(testserver):
    resp = requests.post('%s/json/article-query' % testserver.url, json={})
    assert resp.json() == []


def test_json_article_query_should_accept_valid_request_for_solr(testserver):
    json = {'uniqueIds': ['http://xml.zeit.de/zeit-online/article/zeit']}
    resp = requests.post('%s/json/article-query' % testserver.url, json=json)
    assert resp.ok


def test_json_article_query_should_accept_valid_request_for_elasticserach(
        testserver):
    zeit.web.core.application.FEATURE_TOGGLES.set('elasticsearch_zoca')
    json = {'uniqueIds': ['http://xml.zeit.de/zeit-online/article/zeit']}
    resp = requests.post('%s/json/article-query' % testserver.url, json=json)
    assert resp.ok


def test_json_article_query_should_ignore_broken_hp_for_solr(
        application, monkeypatch):
    monkeypatch.setattr(zeit.cms.interfaces, 'ICMSContent',
                        lambda _, default: default)
    request = mock.MagicMock()
    request.route_url = mock.MagicMock(return_value='/')
    request.json_body = {'uniqueIds': [
        'http://xml.zeit.de/zeit-online/cp-content/article-01']}
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{
        'uniqueId': 'http://xml.zeit.de/zeit-online/cp-content/article-01',
        'uuid': '{urn:uuid:123eca9c-8a28-48e2-962b-96948577d000}'
    }]
    response = zeit.web.core.view_json.json_article_query(request)
    assert not response[0]['on_homepage']


def test_json_article_query_should_ignore_broken_hp_for_elasticsearch(
        application, monkeypatch):
    zeit.web.core.application.FEATURE_TOGGLES.set('elasticsearch_zoca')
    monkeypatch.setattr(zeit.cms.interfaces, 'ICMSContent',
                        lambda _, default: default)
    request = mock.MagicMock()
    request.route_url = mock.MagicMock(return_value='/')
    request.json_body = {'uniqueIds': [
        'http://xml.zeit.de/zeit-online/cp-content/article-01']}
    elasticsearch = zope.component.getUtility(
        zeit.retresco.interfaces.IElasticsearch)
    elasticsearch.resolve_results = False
    elasticsearch.results = [{
        'doc_id': '{urn:uuid:893eca9c-8a28-48e2-962b-96948577111d}',
        'url': '/zeit-online/cp-content/article-01'
    }]
    response = zeit.web.core.view_json.json_article_query(request)
    assert not response[0]['on_homepage']


def test_json_article_query_should_construct_correct_solr_queries(
        application, monkeypatch):
    monkeypatch.setattr(zeit.cms.interfaces, 'ID_NAMESPACE', 'foo')
    request = mock.MagicMock()
    request.json_body = {
        'uniqueIds': ['foo://1', 'foo://2'],
        'uuids': ['30d678d7-d8d7-4eaf-a5c8-f99fa137d69e']
    }
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    search = mock.MagicMock(return_value=[])
    monkeypatch.setattr(solr, 'search', search)
    zeit.web.core.view_json.json_article_query(request)
    args, kw = search.call_args
    assert args[0] == ('(uniqueId:"foo://1" OR uniqueId:"foo://2" OR uuid:'
                       '"{urn:uuid:30d678d7-d8d7-4eaf-a5c8-f99fa137d69e}")')
    assert kw['fq'] == 'comments:(true)'


def test_json_article_query_should_construct_correct_elasticsearch_queries(
        application, monkeypatch):
    zeit.web.core.application.FEATURE_TOGGLES.set('elasticsearch_zoca')
    monkeypatch.setattr(zeit.cms.interfaces, 'ID_NAMESPACE', 'foo')
    request = mock.MagicMock()
    request.json_body = {
        'uniqueIds': ['foo://1', 'foo://2'],
        'uuids': ['30d678d7-d8d7-4eaf-a5c8-f99fa137d69e']
    }
    elasticsearch = zope.component.getUtility(
        zeit.retresco.interfaces.IElasticsearch)
    search = mock.MagicMock(return_value=[])
    monkeypatch.setattr(elasticsearch, 'search', search)
    zeit.web.core.view_json.json_article_query(request)
    args, _ = search.call_args
    assert args[0]['query'] == {
        'bool': {
            'filter': {
                'term': {'payload.document.comments': True}},
            'minimum_should_match': 1,
            'should': [
                {'terms': {'doc_id': [
                    '{urn:uuid:30d678d7-d8d7-4eaf-a5c8-f99fa137d69e}']}},
                {'terms': {'url': ['/://1', '/://2']}}]}}
    assert args[1] == 'payload.document.date_first_released:desc'


def test_json_article_query_should_transform_solr(application):
    request = mock.Mock()
    request.route_url = mock.MagicMock(return_value='//zeit.to/')
    request.json_body = {'uniqueIds': [
        'http://xml.zeit.de/zeit-online/cp-content/article-01',
        'http://xml.zeit.de/zeit-online/cp-content/article-05']}
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
        'uuid': 'my-uuid-article-01'
    }, {
        'date_first_released': '2017-05-07T15:01:26.098814+00:00',
        'date_last_published': '2017-05-07T15:01:26.098814+00:00',
        'keywords': ['kw-4', 'kw-8'],
        'ressort': 'my-ressort',
        'sub_ressort': 'my-sub-ressort',
        'supertitle': 'my-super-title',
        'teaser_text': 'my-teaser-text',
        'title': 'my-title',
        'uniqueId': 'http://xml.zeit.de/zeit-online/cp-content/article-05',
        'uuid': 'my-uuid-article-05'
    }]
    response = zeit.web.core.view_json.json_article_query(request)
    assert response == [{
        'date_first_released': '2017-05-03T15:01:26.098814+00:00',
        'date_last_published': '2017-05-03T15:01:26.098814+00:00',
        'keywords': ['kw-1', 'kw-3', 'kw-8'],
        'lead_article': True,
        'on_homepage': True,
        'ressort': 'my-ressort',
        'sub_ressort': 'my-sub-ressort',
        'supertitle': 'my-super-title',
        'teaser_text': 'my-teaser-text',
        'title': 'my-title',
        'uniqueId': 'http://xml.zeit.de/zeit-online/cp-content/article-01',
        'url': '//zeit.to/zeit-online/cp-content/article-01',
        'uuid': 'my-uuid-article-01'
    }, {
        'date_first_released': '2017-05-07T15:01:26.098814+00:00',
        'date_last_published': '2017-05-07T15:01:26.098814+00:00',
        'keywords': ['kw-4', 'kw-8'],
        'lead_article': False,
        'on_homepage': True,
        'ressort': 'my-ressort',
        'sub_ressort': 'my-sub-ressort',
        'supertitle': 'my-super-title',
        'teaser_text': 'my-teaser-text',
        'title': 'my-title',
        'uniqueId': 'http://xml.zeit.de/zeit-online/cp-content/article-05',
        'url': '//zeit.to/zeit-online/cp-content/article-05',
        'uuid': 'my-uuid-article-05'
    }]


def test_json_article_query_should_transform_elasticsearch(application):
    zeit.web.core.application.FEATURE_TOGGLES.set('elasticsearch_zoca')
    request = mock.Mock()
    request.route_url = mock.MagicMock(return_value='//zeit.to/')
    request.json_body = {'uniqueIds': [
        'http://xml.zeit.de/zeit-online/cp-content/article-01',
        'http://xml.zeit.de/zeit-online/cp-content/article-05']}
    elasticsearch = zope.component.getUtility(
        zeit.retresco.interfaces.IElasticsearch)
    elasticsearch.resolve_results = False
    elasticsearch.results = [{
        'doc_id': '{urn:uuid:893eca9c-8a28-48e2-962b-96948577111d}',
        'payload': {
            'document': {
                'comments_premoderate': False,
                'date_first_released': '2018-04-04T14:54:18.915698+00:00',
                'ressort': 'Sport',
                'sub_ressort': 'Ballsport'},
            'workflow': {
                'date_last_published': '2018-04-11T10:44:08.002988+00:00'}
            },
        'rtr_tags': [
            'Handball',
            'Russland',
            'Watutinki'],
        'supertitle': 'Handball-WM in Russland',
        'teaser': 'Unsere Autorin wollte nun ins deutsche WM-Quartier',
        'title': 'Der Geist von Watutinki',
        'url': '/zeit-online/cp-content/article-01'
    }, {
        'doc_id': '{urn:uuid:123eca9c-8a28-48e2-962b-96948577d000}',
        'url': '/zeit-online/cp-content/article-05'
    }]
    response = zeit.web.core.view_json.json_article_query(request)
    assert response == [{
        'date_first_released': '2018-04-04T14:54:18.915698+00:00',
        'date_last_published': '2018-04-11T10:44:08.002988+00:00',
        'keywords': ['Handball', 'Russland', 'Watutinki'],
        'comments_premoderate': False,
        'lead_article': True,
        'on_homepage': True,
        'ressort': 'Sport',
        'sub_ressort': 'Ballsport',
        'supertitle': 'Handball-WM in Russland',
        'teaser_text': 'Unsere Autorin wollte nun ins deutsche WM-Quartier',
        'title': 'Der Geist von Watutinki',
        'uniqueId': u'http://xml.zeit.de/zeit-online/cp-content/article-01',
        'url': u'//zeit.to/zeit-online/cp-content/article-01',
        'uuid': '{urn:uuid:893eca9c-8a28-48e2-962b-96948577111d}'
    }, {
        'date_first_released': None,
        'date_last_published': None,
        'keywords': [],
        'comments_premoderate': False,
        'lead_article': False,
        'on_homepage': True,
        'ressort': None,
        'sub_ressort': None,
        'teaser_text': None,
        'uniqueId': u'http://xml.zeit.de/zeit-online/cp-content/article-05',
        'url': u'//zeit.to/zeit-online/cp-content/article-05',
        'uuid': '{urn:uuid:123eca9c-8a28-48e2-962b-96948577d000}'
    }]
