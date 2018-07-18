import datetime

import lxml.etree
import mock
import pytz
import zope.component

import zeit.content.cp.interfaces

import zeit.web.core.retresco
import zeit.web.core.solr
import zeit.web.site.area.overview


def get_area(kind, count):
    area = zeit.cms.interfaces.ICMSContent(
        'http://block.vivi.zeit.de/http://xml.zeit.de/news/index#body/id-'
        '6f4ded13-7461-4197-804c-db3d668fa252/id-5fe59e73-e388-42a4-a8d4-'
        '750b0bf96fc2')
    area.kind = kind
    jango = area.values()[0]
    area.clear()
    mixin = zeit.web.site.area.overview.OverviewContentQueryMixin
    for value in mixin.clone_factory(jango, count):
        area.insert(0, value)
    return zope.component.getAdapter(
        area, zeit.content.cp.interfaces.IRenderedArea, kind)


def test_overview_area_should_have_a_sanity_bound_count(application):
    area = get_area('overview', 1)
    assert area.count == zeit.web.site.area.overview.SANITY_BOUND


def test_overview_area_should_produce_correct_date_ranges(
        clock, application, dummy_request):
    clock.freeze(zeit.web.core.date.parse_date(
        '2016-05-10T1:23:59.780412+00:00'))
    area = get_area('overview', 20)
    area.request = dummy_request

    start, finish = area._content_query._date_range()
    assert start == datetime.datetime(2016, 5, 10, tzinfo=pytz.UTC)
    assert finish == datetime.datetime(2016, 5, 11, tzinfo=pytz.UTC)

    dummy_request.GET['date'] = '2016-05-09'
    area = get_area('overview', 20)

    start, finish = area._content_query._date_range()
    assert start == datetime.datetime(2016, 5, 9, tzinfo=pytz.UTC)
    assert finish == datetime.datetime(2016, 5, 10, tzinfo=pytz.UTC)

    dummy_request.GET['date'] = '2016-05-08'
    area = get_area('overview', 20)

    start, finish = area._content_query._date_range()
    assert start == datetime.datetime(2016, 5, 8, tzinfo=pytz.UTC)
    assert finish == datetime.datetime(2016, 5, 9, tzinfo=pytz.UTC)


def test_overview_solr_area_should_overflow_if_necessary(
        application, dummy_request):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
        ({'uniqueId':
          'http://xml.zeit.de/zeit-online/article/01'}) for i in range(3)]
    area = get_area('overview', 1)
    area.automatic_type = 'query'
    assert len(area.values()) == 3

    solr.results = [
        ({'uniqueId':
          'http://xml.zeit.de/zeit-online/article/01'}) for i in range(3)]
    area = get_area('overview', 3)
    area.automatic_type = 'query'
    assert len(area.values()) == 3


def test_overview_elasticsearch_area_should_overflow_if_necessary(
        application, dummy_request):
    es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    es.results = [
        ({'uniqueId':
          'http://xml.zeit.de/zeit-online/article/01'}) for i in range(3)]
    area = get_area('overview', 1)
    assert len(area.values()) == 3

    es.results = [
        ({'uniqueId':
          'http://xml.zeit.de/zeit-online/article/01'}) for i in range(3)]
    area = get_area('overview', 3)
    assert len(area.values()) == 3


def test_overview_solr_area_should_respect_sanity_bound(
        application, dummy_request, monkeypatch):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
        ({'uniqueId':
          'http://xml.zeit.de/zeit-online/article/01'}) for i in range(10)]
    monkeypatch.setattr(zeit.web.site.area.overview, 'SANITY_BOUND', 5)

    area = get_area('overview', 1)
    area.automatic_type = 'query'
    assert len(area.values()) == 5


def test_overview_elasticsearch_area_should_respect_sanity_bound(
        application, dummy_request, monkeypatch):
    es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    es.results = [
        ({'uniqueId':
          'http://xml.zeit.de/zeit-online/article/01'}) for i in range(10)]
    monkeypatch.setattr(zeit.web.site.area.overview, 'SANITY_BOUND', 5)

    area = get_area('overview', 1)
    assert len(area.values()) == 5


def test_overview_area_clone_factory_should_set_proper_attributes():
    class Foo(mock.Mock):
        __parent__ = object()
        __name__ = object()
        xml = lxml.etree.fromstring('<foo/>')

    mixin = zeit.web.site.area.overview.OverviewContentQueryMixin
    clones = mixin.clone_factory(Foo(), 3)

    assert all(c.xml is Foo.xml for c in clones)
    assert all(c.__parent__ is Foo.__parent__ for c in clones)
    assert all(len(c.__name__) == 36 for c in clones)


def test_overview_should_get_total_pages_from_config(application):
    area = get_area('overview', 1)
    assert area.total_pages == 30


def test_overview_should_have_page_info(application, clock, dummy_request):
    clock.freeze(zeit.web.core.date.parse_date(
        '2016-05-10T1:23:59.780412+00:00'))
    area = get_area('overview', 1)
    area.request = dummy_request
    pi = area.page_info(1)
    assert pi['label'] == '10.05.2016'
    assert not pi['url'].endswith('date=2016-05-10')

    pi = area.page_info(2)
    assert pi['label'] == '09.05'
    assert pi['url'].endswith('date=2016-05-09')


def test_overview_should_have_https_links(application, clock, dummy_request):
    clock.freeze(zeit.web.core.date.parse_date(
        '2016-05-10T1:23:59.780412+00:00'))
    zeit.web.core.application.FEATURE_TOGGLES.unset('https')
    area = get_area('overview', 1)
    area.request = dummy_request
    pi = area.page_info(1)
    assert pi['url'].startswith('http://')

    zeit.web.core.application.FEATURE_TOGGLES.set('https')
    area = get_area('overview', 1)
    area.request = dummy_request
    pi = area.page_info(1)
    assert pi['url'].startswith('https://')


def test_overview_should_render_cover_image_from_solr_result(testbrowser):
    volume = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/2016/01/ausgabe')
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{
        'uniqueId': volume.uniqueId,
        'year': volume.year,
        'volume': volume.volume,
        'cover_printcover': volume.get_cover('printcover').uniqueId,
    }]
    browser = testbrowser('/2016/index-solr')
    assert '/2016-09/test-printcover' in browser.cssselect(
        '.teaser-volume-overview img')[0].get('src')


def test_default_teaser_should_not_expose_ranking_area_proxies(
        testbrowser, data_solr, monkeypatch):
    log = mock.Mock()
    monkeypatch.setattr(zeit.web.core.solr, 'log', log)

    monkeypatch.setattr(
        zeit.web.core.comments.Community, 'get_comment_counts',
        lambda *args: {x: 1 for x in args})

    browser = testbrowser('/dynamic/paul-auster')
    assert len(browser.cssselect('.cp-area--ranking article')) == 10
    assert 'teaser-small__byline' in browser.contents

    log = log.debug.call_args_list
    assert all('ProxyExposed' not in a[0][0] for a in log), str(log)
