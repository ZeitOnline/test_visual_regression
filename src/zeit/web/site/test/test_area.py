import mock
import lxml.etree
import zope.component

import zeit.content.cp.interfaces

import zeit.web.core.area.ranking
import zeit.web.core.utils
import zeit.web.site.area.overview


def get_area(kind, count):
    area = zeit.cms.interfaces.ICMSContent(
        'http://block.vivi.zeit.de/http://xml.zeit.de/news/index#body/id-'
        '6f4ded13-7461-4197-804c-db3d668fa252/id-5fe59e73-e388-42a4-a8d4-'
        '750b0bf96fc2')
    area.kind = kind
    jango = area.values()[0]
    area.clear()
    for value in zeit.web.site.area.overview.DateContentQuery.clone_factory(
            jango, count):
        area.insert(0, value)
    return zope.component.getAdapter(
        area, zeit.content.cp.interfaces.IRenderedArea, kind)


def test_overview_area_should_have_a_sanity_bound_count(application):
    area = get_area('overview', 1)
    assert area.count == zeit.web.site.area.overview.SANITY_BOUND


def test_overview_area_should_produce_correct_ranges(
        clock, application, dummy_request):
    clock.freeze(zeit.web.core.date.parse_date(
        '2016-05-10T1:23:59.780412+00:00'))
    area = get_area('overview', 20)
    area.request = dummy_request

    assert area._content_query._range_query() == (
        'date_first_released:[2016-05-10T00:00:00Z '
        'TO 2016-05-11T00:00:00Z]')

    dummy_request.GET['date'] = '2016-05-09'
    area = get_area('overview', 20)

    assert area._content_query._range_query() == (
        'date_first_released:[2016-05-09T00:00:00Z '
        'TO 2016-05-10T00:00:00Z]')

    dummy_request.GET['date'] = '2016-05-08'
    area = get_area('overview', 20)

    assert area._content_query._range_query() == (
        'date_first_released:[2016-05-08T00:00:00Z '
        'TO 2016-05-09T00:00:00Z]')


def test_overview_area_should_overflow_if_necessary(
        application, dummy_request):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
        ({'uniqueId':
          'http://xml.zeit.de/zeit-online/article/01'}) for i in range(3)]
    area = get_area('overview', 1)
    assert len(area.values()) == 3

    solr.results = [
        ({'uniqueId':
          'http://xml.zeit.de/zeit-online/article/01'}) for i in range(3)]
    area = get_area('overview', 3)
    assert len(area.values()) == 3


def test_overview_area_should_respect_sanity_bound(
        application, dummy_request, monkeypatch):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
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

    clones = zeit.web.site.area.overview.DateContentQuery.clone_factory(
        Foo(), 3)

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
    assert pi['page_label'] == '10.05.2016'
    assert pi['remove_get_param'] == 'date'
    assert pi['append_get_param']['date'] == '2016-05-10'

    pi = area.page_info(2)
    assert pi['page_label'] == '09.05'
    assert pi['remove_get_param'] == 'date'
    assert pi['append_get_param']['date'] == '2016-05-09'


def test_default_teaser_should_not_expose_ranking_area_proxies(
        testbrowser, datasolr, monkeypatch):
    log = mock.Mock()
    monkeypatch.setattr(zeit.web.core.utils, 'log', log)

    monkeypatch.setattr(
        zeit.web.core.comments.Community, 'get_comment_counts',
        lambda *args: {x: 1 for x in args})

    browser = testbrowser('/dynamic/paul-auster')
    assert len(browser.cssselect('.cp-area--ranking article')) == 10
    assert 'teaser-small__byline' in browser.contents

    log = log.debug.call_args_list
    assert all('ProxyExposed' not in a[0][0] for a in log), str(log)


def test_tms_query_should_not_expose_ranking_area_proxies(
        testbrowser, monkeypatch, request):
    previous = zope.component.queryUtility(zeit.retresco.interfaces.ITMS)
    if previous:
        request.addfinalizer(lambda: zope.component.provideUtility(previous))
    zope.component.provideUtility(zeit.web.core.utils.DataTMS())

    log = mock.Mock()
    monkeypatch.setattr(zeit.web.core.utils, 'log', log)

    monkeypatch.setattr(
        zeit.web.core.comments.Community, 'get_comment_counts',
        lambda *args: {x: 1 for x in args})

    browser = testbrowser('/dynamic/tms-berlin')
    assert len(browser.cssselect('.cp-area--ranking article')) == 25

    log = log.debug.call_args_list
    assert all('ProxyExposed' not in a[0][0] for a in log), str(log)


def test_elasticsearch_query_should_not_expose_ranking_area_proxies(
        testbrowser, monkeypatch, request):
    previous = zope.component.queryUtility(
        zeit.retresco.interfaces.IElasticsearch)
    if previous:
        request.addfinalizer(lambda: zope.component.provideUtility(previous))
    zope.component.provideUtility(zeit.web.core.utils.DataES())

    log = mock.Mock()
    monkeypatch.setattr(zeit.web.core.utils, 'log', log)

    monkeypatch.setattr(
        zeit.web.core.comments.Community, 'get_comment_counts',
        lambda *args: {x: 1 for x in args})

    browser = testbrowser('/dynamic/es-berlin')
    assert len(browser.cssselect('.cp-area--ranking article')) == 25

    log = log.debug.call_args_list
    assert all('ProxyExposed' not in a[0][0] for a in log), str(log)
