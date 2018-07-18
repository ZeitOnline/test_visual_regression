import zope.component

import zeit.content.cp.centerpage
import zeit.retresco.content
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


def test_es_based_areas_use_results_directly_and_dont_resolve_content(
        application, dummy_request):
    es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    es.results = [{'uniqueId': 'http://xml.zeit.de/zeit-online/article/01'}]
    tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
    tms.results = [{'uniqueId': 'http://xml.zeit.de/zeit-online/article/01'}]

    cp = zeit.content.cp.centerpage.CenterPage()
    cp.uniqueId = 'http://xml.zeit.de/testcp'
    area = cp.body.create_item('region').create_item('area')
    area.kind = 'ranking'
    area.count = 1
    area.automatic_type = 'elasticsearch-query'
    # actual value is irrelevant, results are mocked
    area.elasticsearch_raw_query = '{"query": {"match_all": {}}}'
    area.automatic = True

    area = zeit.web.core.centerpage.get_area(area)
    content = list(area.values()[0])[0]
    assert isinstance(content, zeit.retresco.content.Content)

    area.automatic_type = 'custom'
    # actual value is irrelevant, results are mocked
    area.query = (('channels', 'Wissen', None))
    area = zeit.web.core.centerpage.get_area(area)
    content = list(area.values()[0])[0]
    assert isinstance(content, zeit.retresco.content.Content)

    area.automatic_type = 'topicpage'
    # actual value is irrelevant, results are mocked
    area.referenced_topicpage = 'berlin'
    area = zeit.web.core.centerpage.get_area(area)
    content = list(area.values()[0])[0]
    assert isinstance(content, zeit.retresco.content.Content)
