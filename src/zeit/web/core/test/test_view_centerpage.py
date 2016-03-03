import datetime
import pytest
import requests
import zope.component

import zeit.content.cp.centerpage
import zeit.cms.interfaces

import zeit.web.core.centerpage
import zeit.web.core.view_centerpage


def test_centerpage_should_return_jsonp_with_timestamp_if_released(
        testbrowser):
    # published page returns its pubdate
    browser = testbrowser(
        '/json_update_time/zeit-online/main-teaser-setup?callback=foo123')
    pubstring = (
        '/**/foo123({"last_published_semantic": '
        '"2014-11-18T12:18:27.293179+00:00", '
        '"last_published": "2014-11-18T12:18:27.293179+00:00"});')
    assert browser.headers.type == 'application/javascript'
    assert pubstring == browser.contents


def test_centerpage_should_return_jsonp_with_timestamp_if_not_released(
        testbrowser):
    # published page returns empty string
    browser = testbrowser(
        '/json_update_time/zeit-online/teaser-serie-setup?callback=foo123')
    pubstring = (
        '/**/foo123({"last_published_semantic": null, '
        '"last_published": null});')
    assert browser.headers.type == 'application/javascript'
    assert pubstring == browser.contents


def test_json_update_time_handler_should_set_exipration_header(testbrowser):
    browser = testbrowser(
        '/json_update_time/zeit-online/main-teaser-setup?cb=123')
    assert browser.headers.get('cache-control') == 'max-age=5'


def test_centerpage_should_aggregate_all_teasers_correctly(
        application, dummy_request):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2')
    items = list(zeit.web.core.view_centerpage.Centerpage(cp, dummy_request))
    assert items[0].uniqueId == (
        'http://xml.zeit.de/zeit-magazin/test-cp/essen-geniessen-spargel-lamm')
    assert len(items) == 19


def test_centerpage_should_evaluate_automatic_areas_for_teasers(
        application, dummy_request):
    cp = zeit.content.cp.centerpage.CenterPage()
    cp.uniqueId = 'http://xml.zeit.de/testcp'
    other = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2')
    area = cp.body.create_item('region').create_item('area')
    area.kind = 'duo'  # Fixture config default teaser layout
    area.automatic_type = 'centerpage'
    area.referenced_cp = other
    area.count = 5
    area.automatic = True
    items = list(zeit.web.core.view_centerpage.Centerpage(cp, dummy_request))
    assert items[0].uniqueId == (
        'http://xml.zeit.de/zeit-magazin/test-cp/essen-geniessen-spargel-lamm')
    assert len(items) == area.count


def test_nonexistent_content_should_be_skipped(application, workingcopy):
    other = zeit.content.cp.centerpage.CenterPage()
    teaser = other.body.create_item('region').create_item('area').create_item(
        'teaser')
    teaser.insert(0, 'http://xml.zeit.de/zeit-online/article/01')
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    repository['testcp'] = other
    del repository['zeit-online']['article']['01']

    cp = zeit.content.cp.centerpage.CenterPage()
    # cp.uniqueId = 'http://xml.zeit.de/testcp'
    area = cp.body.create_item('region').create_item('area')
    area.kind = 'duo'  # Fixture config default teaser layout
    area.automatic_type = 'centerpage'
    area.referenced_cp = other
    area.count = 1
    area.automatic = True
    assert not zeit.content.cp.interfaces.IRenderedArea(area).values()


def test_centerpage_should_collect_teaser_counts_from_community(
        application, dummy_request, mockserver_factory):
    cp_counts = """<?xml version="1.0" encoding="UTF-8"?>
    <nodes>
         <node comment_count="129"
               url="/zeit-magazin/test-cp/essen-geniessen-spargel-lamm"/>
    </nodes>
    """
    mockserver_factory(cp_counts)
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2')
    view = zeit.web.core.view_centerpage.Centerpage(cp, dummy_request)
    path, count = view.comment_counts.items()[0]
    assert '/zeit-magazin/test-cp/essen-geniessen-spargel-lamm' in path
    assert count == '129'


def test_centerpage_should_have_smaxage(testserver, testbrowser):
    browser = testbrowser('/zeit-online/slenderized-index')
    assert browser.headers.dict['s-maxage'] == '21600'


def test_rendering_centerpage_should_cache_region_and_area_values(
        application, monkeypatch):
    call_count = {'region': 0, 'area': 0}

    def count_values_region(self):
        call_count['region'] += 1
        return region_values(self)
    region_values = zeit.content.cp.area.Region.values
    monkeypatch.setattr(
        zeit.content.cp.area.Region, 'values', count_values_region)

    def count_values_area(self):
        call_count['area'] += 1
        return area_values(self)
    area_values = zeit.content.cp.area.Area.values
    monkeypatch.setattr(
        zeit.content.cp.area.Area, 'values', count_values_area)

    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index')
    rendered = zeit.web.core.centerpage.IRendered(cp.body['feature'])
    for i in range(10):
        rendered.values()[0].values()
    assert call_count['region'] == 1
    # Region has 2 Areas.
    assert call_count['area'] == 2


def test_ranking_pagination_should_redirect_page_one(testserver):
    resp = requests.get('%s/thema/test?p=1' % testserver.url,
                        allow_redirects=False)
    assert resp.headers['location'] == '%s/thema/test' % testserver.url
    assert resp.status_code == 301


@pytest.mark.xfail(reason='Not implemented yet.')
def test_ranking_pagination_should_not_find_out_of_scope_page(testserver):
    resp = requests.get('%s/thema/test?p=3214' % testserver.url,
                        allow_redirects=False)
    assert resp.url == '%s/thema/test?p=3214' % testserver.url
    assert resp.status_code == 404


def test_ranking_pagination_should_omit_default_page_param(testbrowser):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
        {'uniqueId': 'http://xml.zeit.de/artikel/{:0>2d}'.format(i % 10 + 1)}
        for i in range(12)]
    browser = testbrowser('/thema/test?p=2')
    prev = browser.cssselect('head link[rel="prev"]')[0]
    link = browser.cssselect('.pager__pages a')[0]
    assert prev.get('href').endswith('/thema/test')
    assert link.get('href').endswith('/thema/test')


def test_cp_should_include_keyword_entity_type_in_detailed_content_type(
        application, dummy_request):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/dynamic/angela-merkel')
    view = zeit.web.core.view_centerpage.Centerpage(cp, dummy_request)
    assert view.detailed_content_type == 'centerpage.centerpage.person'

def test_cp_should_render_raw_code(testbrowser):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/raw_code')
    code = cp[0][0][0].raw_code.replace('<code>', '').replace('</code>', '')
    browser = testbrowser('/zeit-online/raw_code')
    assert browser.cssselect('code')[0].text == code

#@pytest.mark.skipif(datetime.datetime.now() < datetime.datetime(2016, 3, 8),
#                    reason='Should work when )
