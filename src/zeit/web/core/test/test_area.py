import pyramid.threadlocal
import zope.component

import zeit.content.cp.centerpage
import zeit.solr.interfaces

import zeit.web.core.centerpage


def test_ranking_area_with_automatic_false_has_zero_hits(application):
    cp = zeit.content.cp.centerpage.CenterPage()
    cp.uniqueId = 'http://xml.zeit.de/testcp'
    area = cp.body.create_item('region').create_item('area')
    area.kind = 'ranking'
    area.count = 1
    area.automatic_type = 'query'
    area.raw_query = 'any'
    area.automatic = False
    area = zeit.web.core.centerpage.get_area(area)
    assert area.hits == 0


def test_ranking_area_works_with_channel_query(
        application, dummy_request, monkeypatch):
    monkeypatch.setattr(
        pyramid.threadlocal, 'get_current_request', dummy_request)
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId': 'http://xml.zeit.de/zeit-online/article/01'}]
    cp = zeit.content.cp.centerpage.CenterPage()
    cp.uniqueId = 'http://xml.zeit.de/testcp'
    area = cp.body.create_item('region').create_item('area')
    area.kind = 'ranking'
    area.count = 1
    area.automatic_type = 'query'
    area.raw_query = 'any'
    area.automatic = True
    area = zeit.web.core.centerpage.get_area(area)
    assert len(area.values()) == 1
