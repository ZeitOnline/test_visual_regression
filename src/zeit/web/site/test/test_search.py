# -*- coding: utf-8 -*-
import datetime
import json

import pytest
import zope.component

import zeit.cms.interfaces
import zeit.content.cp.interfaces

import zeit.web.core.centerpage
import zeit.web.core.utils
import zeit.web.site.module.search_form


@pytest.fixture(scope='function')
def search_form(application, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/suche/index')
    block = zeit.web.core.utils.find_block(
        context, module='search-form')
    return zeit.web.core.centerpage.get_module(block)


@pytest.fixture(scope='function')
def search_area(application, dummy_request, monkeypatch):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/suche/index')
    area = zeit.web.core.utils.find_block(
        context, attrib='area', kind='ranking')
    monkeypatch.setattr(area, 'automatic_type', 'query')
    return zeit.web.core.centerpage.get_area(area)


@pytest.fixture(scope='function')
def elasticsearch_area(application, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/suche/index')
    area = zeit.web.core.utils.find_block(
        context, attrib='area', kind='ranking')
    return zeit.web.core.centerpage.get_area(area)


def test_search_form_should_allow_empty_search_term(
        dummy_request, search_form):
    dummy_request.GET['q'] = ''
    assert search_form.search_term is None


def test_search_form_should_allow_valid_search_term(
        dummy_request, search_form):
    dummy_request.GET['q'] = 'pfannkuchen AND ahornsirup'
    assert search_form.search_term == 'pfannkuchen AND ahornsirup'


def test_search_form_should_allow_empty_type_setting(
        dummy_request, search_form):
    dummy_request.GET['type'] = ''
    assert search_form.types == ['article', 'gallery', 'video']


def test_search_form_should_filter_type_settings(
        dummy_request, search_form):
    dummy_request.GET.add('type', 'article')
    dummy_request.GET.add('type', 'pfannkuchen')
    assert search_form.types == ['article']


def test_search_form_should_allow_empty_mode_setting(
        dummy_request, search_form):
    dummy_request.GET['mode'] = ''
    assert search_form.mode is None


def test_search_form_should_ignore_invalid_mode_setting(
        dummy_request, search_form):
    dummy_request.GET['mode'] = 'pfannkuchen'
    assert search_form.mode is None


def test_search_form_should_allow_valid_mode_setting(
        dummy_request, search_form):
    dummy_request.GET['mode'] = '1y'
    assert search_form.mode == '1y'


def test_search_form_should_default_to_recency_sort_order(
        dummy_request, search_form):
    dummy_request.GET['q'] = ''
    dummy_request.GET['sort'] = ''
    assert search_form.order == 'aktuell'


def test_search_form_should_default_to_recency_sort_order_with_query(
        dummy_request, search_form):
    dummy_request.GET['q'] = 'foo'
    dummy_request.GET['sort'] = ''
    assert search_form.order == 'aktuell'


def test_search_form_should_sort_valid_queries_by_relevancy(
        dummy_request, search_form):
    dummy_request.GET['q'] = 'pfannkuchen'
    dummy_request.GET['sort'] = ''
    assert search_form.order == 'aktuell'


def test_search_form_should_ignore_invalid_sort_orders(
        dummy_request, search_form):
    dummy_request.GET['q'] = 'pfannkuchen'
    dummy_request.GET['sort'] = 'pfannkuchen'
    assert search_form.order == 'aktuell'


def test_search_form_should_allow_valid_search_order_aktuell(
        dummy_request, search_form):
    dummy_request.GET['q'] = 'pfannkuchen'
    dummy_request.GET['sort'] = 'aktuell'
    assert search_form.order == 'aktuell'


def test_search_form_should_allow_valid_search_order_relevanz(
        dummy_request, search_form):
    dummy_request.GET['q'] = 'pfannkuchen'
    dummy_request.GET['sort'] = 'relevanz'
    assert search_form.order == 'relevanz'


def test_search_form_should_create_valid_empty_solr_query(search_form):
    assert search_form.raw_query == (
        'type:(article OR gallery OR video) '
        'NOT product_id:(News OR afp OR SID OR ADV) '
        'NOT ressort:(Administratives OR News OR Aktuelles) '
        'NOT expires:[* TO NOW]')


def test_search_form_should_make_valid_empty_elasticsearch_query(search_form):
    assert json.loads(search_form.elasticsearch_raw_query) == {'query': {
        u'bool': {
            u'must': [{
                u'match_all': {}
            }, {
                u'terms': {
                    u'payload.meta.type': [
                        u'article', u'gallery', u'video']}
            }, {
                u'term': {u'payload.workflow.published': True}
            }],
            u'must_not': [{
                u'terms': {
                    u'payload.workflow.product-id': [
                        u'ADV', u'News', u'SID', u'afp']}
            }, {
                u'terms': {
                    u'payload.document.ressort': [
                        u'Administratives', u'Aktuelles', u'News']}
            }]
        }
    }}


def test_search_form_should_create_valid_fulltext_solr_query(
        dummy_request, search_form):
    dummy_request.GET['q'] = u'pfannkuchen OR müsli'
    assert search_form.raw_query == (
        u'{!boost b=recip(ms(NOW,last-semantic-change),3.16e-11,1,1)}'
        u'{!type=IntrafindQueryParser}(pfannkuchen OR müsli) '
        u'type:(article OR gallery OR video) '
        u'NOT product_id:(News OR afp OR SID OR ADV) '
        u'NOT ressort:(Administratives OR News OR Aktuelles) '
        u'NOT expires:[* TO NOW]')


def test_search_form_should_create_valid_fulltext_elasticsearch_query(
        dummy_request, search_form):
    dummy_request.GET['q'] = u'pfannkuchen OR müsli'
    assert json.loads(search_form.elasticsearch_raw_query) == {'query': {
        u'bool': {
            u'must': [{
                u'simple_query_string': {
                    u'query': u'pfannkuchen OR müsli',
                    u'fields': search_form.FIELDS}
            }, {
                u'terms': {
                    u'payload.meta.type': [
                        u'article', u'gallery', u'video']}
            }, {
                u'term': {u'payload.workflow.published': True}
            }],
            u'must_not': [{
                u'terms': {
                    u'payload.workflow.product-id': [
                        u'ADV', u'News', u'SID', u'afp']}
            }, {
                u'terms': {
                    u'payload.document.ressort': [
                        u'Administratives', u'Aktuelles', u'News']}
            }]
        }
    }}


def test_search_form_should_create_valid_date_range_solr_query(
        dummy_request, search_form, clock, monkeypatch):
    clock.freeze(datetime.datetime(2010, 3, 2))
    monkeypatch.setattr(zeit.find.daterange, 'datetime', clock)
    dummy_request.GET['mode'] = '1y'
    assert search_form.raw_query == (
        'last-semantic-change:[2009-03-01T00:00:00Z TO 2010-03-02T00:00:00Z] '
        'type:(article OR gallery OR video) '
        'NOT product_id:(News OR afp OR SID OR ADV) '
        'NOT ressort:(Administratives OR News OR Aktuelles) '
        'NOT expires:[* TO NOW]')


def test_search_form_should_create_valid_date_range_elasticsearch_query(
        dummy_request, search_form):
    dummy_request.GET['mode'] = '1y'
    assert json.loads(search_form.elasticsearch_raw_query) == {'query': {
        u'bool': {
            u'must': [{
                u'match_all': {}
            }, {
                u'terms': {
                    u'payload.meta.type': [
                        u'article', u'gallery', u'video']}
            }, {
                u'term': {u'payload.workflow.published': True}
            }, {
                u'range': {
                    u'payload.document.last-semantic-change': {
                        u'gte': u'now-1y'}}
            }],
            u'must_not': [{
                u'terms': {
                    u'payload.workflow.product-id': [
                        u'ADV', u'News', u'SID', u'afp']}
            }, {
                u'terms': {
                    u'payload.document.ressort': [
                        u'Administratives', u'Aktuelles', u'News']}
            }]
        }
    }}


def test_search_form_should_create_valid_type_restricted_solr_query(
        dummy_request, search_form):
    dummy_request.GET.add('type', 'article')
    dummy_request.GET.add('type', 'gallery')
    assert search_form.raw_query == (
        'type:(article OR gallery) '
        'NOT product_id:(News OR afp OR SID OR ADV) '
        'NOT ressort:(Administratives OR News OR Aktuelles) '
        'NOT expires:[* TO NOW]')


def test_search_form_should_create_valid_type_restricted_elasticsearch_query(
        dummy_request, search_form):
    dummy_request.GET.add('type', 'article')
    dummy_request.GET.add('type', 'gallery')
    assert json.loads(search_form.elasticsearch_raw_query) == {'query': {
        u'bool': {
            u'must': [{
                u'match_all': {}
            }, {
                u'terms': {
                    u'payload.meta.type': [u'article', u'gallery']}
            }, {
                u'term': {u'payload.workflow.published': True}
            }],
            u'must_not': [{
                u'terms': {
                    u'payload.workflow.product-id': [
                        u'ADV', u'News', u'SID', u'afp']}
            }, {
                u'terms': {
                    u'payload.document.ressort': [
                        u'Administratives', u'Aktuelles', u'News']}
            }]
        }
    }}


def test_search_form_should_boost_elasticsearch_query_by_relevancy(
        dummy_request, search_form):
    dummy_request.GET['q'] = 'beans AND toast'
    dummy_request.GET['sort'] = 'relevanz'
    assert json.loads(search_form.elasticsearch_raw_query) == {'query': {
        u'bool': {
            u'must': [{
                u'function_score': {
                    u'query': {
                        u'simple_query_string': {
                            u'query': u'beans AND toast',
                            u'fields': search_form.FIELDS}},
                    u'linear': {
                        u'payload.document.date-last-modified': {
                            u'scale': u'365d'
                        }
                    }
                }
            }, {
                u'terms': {u'payload.meta.type': [
                    u'article', u'gallery', u'video']}
            }, {
                u'term': {u'payload.workflow.published': True}
            }],
            u'must_not': [{
                u'terms': {
                    u'payload.workflow.product-id': [
                        u'ADV', u'News', u'SID', u'afp']}
            }, {
                u'terms': {
                    u'payload.document.ressort': [
                        u'Administratives', u'Aktuelles', u'News']}
            }]
        }
    }}


def test_search_area_should_delegate_sort_order_to_search_form(
        search_form, search_area, dummy_request):
    dummy_request.GET['q'] = 'irgendetwas'
    dummy_request.GET['sort'] = 'publikation'
    assert search_area.sort_order == 'publikation'


def test_ranking_area_should_use_default_order_when_no_search_form(
        application):
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/dynamic/umbrien')
    area = zeit.web.core.centerpage.get_area(zeit.web.core.utils.find_block(
        cp, attrib='area', kind='ranking'))
    assert area.raw_order == zeit.content.cp.interfaces.IArea[
        'raw_order'].default


def test_ranking_area_should_use_its_own_query_when_no_search_form(
        application):
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/dynamic/umbrien')
    area = zeit.web.core.centerpage.get_area(zeit.web.core.utils.find_block(
        cp, attrib='area', kind='ranking'))
    assert 'umbrien' in area.raw_query


def test_search_area_should_produce_valid_set_of_solr_results(
        search_area):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId': 'http://xml.zeit.de/arbeit/article/quotes'}]
    assert list(search_area.values()[0])[0].uniqueId == (
        'http://xml.zeit.de/arbeit/article/quotes')


def test_search_area_should_produce_valid_set_of_elasticsearch_results(
        elasticsearch_area):
    es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    es.results = [{'uniqueId': 'http://xml.zeit.de/campus/article/simple'}]
    assert list(elasticsearch_area.values()[0])[0].uniqueId == (
        'http://xml.zeit.de/campus/article/simple')


def test_empty_solr_result_should_produce_zero_hit_counter(search_area):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = []
    assert search_area.hits == 0


def test_empty_elasticsearch_result_should_produce_zero_hit_counter(
        elasticsearch_area):
    es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    es.results = []
    assert elasticsearch_area.hits == 0


def test_successful_solr_result_should_produce_nonzero_hit_counter(
        search_area):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId': ('http://xml.zeit.de/article/0%s' % i)
                     } for i in range(1, 74)]
    assert search_area.hits == 73


def test_successful_elasticsearch_result_should_produce_nonzero_hit_counter(
        elasticsearch_area):
    es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    es.results = [{'url': ('http://xml.zeit.de/article/0%s' % i)
                   } for i in range(1, 43)]
    assert elasticsearch_area.hits == 42


def test_empty_solr_result_should_produce_valid_resultset(search_area):
    assert len([a for b in search_area.values() for a in b if b]) == 0


def test_empty_elasticsearch_result_should_produce_valid_resultset(
        elasticsearch_area):
    assert len([a for b in elasticsearch_area.values() for a in b if b]) == 0


def get_result_dict(unique_id):
    return {
        'date_last_published': '2015-07-01T09:50:42Z',
        'product_id': 'ZEI',
        'supertitle': 'Lorem ipsum',
        'title': 'Lorem ipsum',
        'uniqueId': unique_id}


def test_successful_solr_result_should_produce_valid_resultset(search_area):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    uid = 'http://xml.zeit.de/zeit-magazin/article/0%s'
    solr.results = [{'uniqueId': (uid % i)} for i in range(1, 9)]
    assert len([a for b in search_area.values() for a in b if b]) == 8
    solr.results = [{'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/01'}]
    block = iter(search_area.values()).next()
    assert zeit.content.cp.interfaces.IAutomaticTeaserBlock.providedBy(block)
    assert zeit.cms.interfaces.ICMSContent.providedBy(iter(block).next())


def test_successful_elasticsearch_result_should_produce_valid_resultset(
        elasticsearch_area):
    es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    uid = 'http://xml.zeit.de/zeit-magazin/article/0%s'
    es.results = [{'uniqueId': (uid % i)} for i in range(1, 9)]
    assert len([a for b in elasticsearch_area.values() for a in b if b]) == 8
    es.results = [{'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/01'}]
    block = iter(elasticsearch_area.values()).next()
    assert zeit.content.cp.interfaces.IAutomaticTeaserBlock.providedBy(block)
    assert zeit.cms.interfaces.ICMSContent.providedBy(iter(block).next())


def test_successful_search_result_should_render_in_browser(
        testbrowser, data_es):
    browser = testbrowser('/suche/index')
    assert browser.cssselect('.cp-area--ranking .teaser-small')
