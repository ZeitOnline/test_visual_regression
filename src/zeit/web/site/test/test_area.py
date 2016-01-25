import mock
import lxml.etree
import zope.component

import zeit.content.cp.automatic
import zeit.content.cp.interfaces

import zeit.web.site.area.overview
import zeit.web.site.area.ranking
import zeit.web.core.utils


def get_area(kind, count):
    area = zeit.cms.interfaces.ICMSContent(
        'http://block.vivi.zeit.de/http://xml.zeit.de/news/index#body/id-'
        '6f4ded13-7461-4197-804c-db3d668fa252/id-5fe59e73-e388-42a4-a8d4-'
        '750b0bf96fc2')
    area.kind = kind
    jango = area.values()[0]
    area.clear()
    for value in zeit.web.site.area.overview.Overview.clone_factory(
            jango, count):
        area.insert(0, value)
    return zope.component.getAdapter(
        area, zeit.content.cp.interfaces.IRenderedArea, kind)


def test_overview_area_should_have_a_sanity_bound_count(application):
    area = get_area('overview', 1)
    assert area.count == zeit.web.site.area.overview.SANITY_BOUND


def test_overview_area_should_overflow_if_necessary(
        application, dummy_request, monkeypatch):

    def qs(self, *args):
        self.hits = 3

    monkeypatch.setattr(zeit.web.site.area.ranking.Ranking, '_query_solr', qs)

    area = get_area('overview', 1)
    area._query_solr('', '')
    assert len(area.context.values()) == 3

    area = get_area('overview', 3)
    area._query_solr('', '')
    assert len(area.context.values()) == 3


def test_overview_area_should_respect_sanity_bound(
        application, dummy_request, monkeypatch):

    def qs(self, *args):
        self.hits = 10

    monkeypatch.setattr(zeit.web.site.area.ranking.Ranking, '_query_solr', qs)
    monkeypatch.setattr(zeit.web.site.area.overview, 'SANITY_BOUND', 5)

    area = get_area('overview', 1)
    area._query_solr('', '')
    assert len(area.context.values()) == 5


def test_overview_area_clone_factory_should_set_proper_attributes():
    class Foo(mock.Mock):
        __parent__ = object()
        __name__ = object()
        xml = lxml.etree.fromstring('<foo/>')

    clones = zeit.web.site.area.overview.Overview.clone_factory(Foo(), 3)

    assert all(c.xml is Foo.xml for c in clones)
    assert all(c.__parent__ is Foo.__parent__ for c in clones)
    assert all(len(c.__name__) == 36 for c in clones)


def test_default_teaser_should_not_expose_ranking_area_proxies(
        testbrowser, datasolr, monkeypatch):
    log = mock.Mock()
    monkeypatch.setattr(zeit.web.core.utils, 'log', log)

    browser = testbrowser('/dynamic/paul-auster')
    assert len(browser.cssselect('.cp-area--ranking .teaser-small')) == 10

    assert all('ProxyExposed' not in a[0][0] for a in log.debug.call_args_list)


def test_get_area_should_recognize_zmo_parquet(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/journalistic-formats-zmo')
    area = zeit.web.core.utils.find_block(
        context, 'area', area='id-c52657e6-7494-46d9-86d4-90a88775090c')
    assert zeit.web.core.centerpage.get_area(area).kind == 'zmo-parquet'
