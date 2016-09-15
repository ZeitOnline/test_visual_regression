# -*- coding: utf-8 -*-
import lxml.etree
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
        'http://xml.zeit.de/zeit-magazin/test-cp-legacy/test-cp-zmo-2')
    items = list(zeit.web.core.view_centerpage.Centerpage(cp, dummy_request))
    assert items[0].uniqueId == (
        'http://xml.zeit.de/zeit-magazin/article/essen-geniessen-spargel-lamm')
    assert len(items) == 19


def test_centerpage_should_evaluate_automatic_areas_for_teasers(
        application, dummy_request):
    cp = zeit.content.cp.centerpage.CenterPage()
    cp.uniqueId = 'http://xml.zeit.de/testcp'
    other = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp-legacy/test-cp-zmo-2')
    area = cp.body.create_item('region').create_item('area')
    area.kind = 'duo'  # Fixture config default teaser layout
    area.automatic_type = 'centerpage'
    area.referenced_cp = other
    area.count = 5
    area.automatic = True
    items = list(zeit.web.core.view_centerpage.Centerpage(cp, dummy_request))
    assert items[0].uniqueId == (
        'http://xml.zeit.de/zeit-magazin/article/essen-geniessen-spargel-lamm')
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
               url="/zeit-magazin/article/essen-geniessen-spargel-lamm"/>
    </nodes>
    """
    mockserver_factory(cp_counts)
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp-legacy/test-cp-zmo-2')
    view = zeit.web.core.view_centerpage.Centerpage(cp, dummy_request)
    path, count = view.comment_counts.items()[0]
    assert '/zeit-magazin/article/essen-geniessen-spargel-lamm' in path
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
        {'uniqueId': ('http://xml.zeit.de/zeit-magazin/article/{:0>2d}'
                      .format(i % 10 + 1))}
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


def test_transparent_image_renders_fill_color_for_teaserlayouts(testbrowser):
    # Most teaserlayouts don't support transparent images, so by default we
    # ask for an image with a fill_color. (We look at two teasers in this test
    # to show that the teaser layout doesn't really matter -- it will matter
    # only for special cases like zmo-card, which get their own test).
    browser = testbrowser('/zeit-online/transparent-teaserimage')
    assert 'ccddee' in (
        browser.cssselect('.teaser-large img')[0].attrib['data-src'])
    assert 'ccddee' in (
        browser.cssselect('.teaser-small-minor img')[0].attrib['data-src'])


def test_next_page_url_should_be_set_on_page_based_paginated_centerpages(
        application, dummy_request):

    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
        ({'uniqueId':
         'http://xml.zeit.de/zeit-magazin/article/01'}) for i in range(82)]

    # make sure that it's beyond our default pager slot size
    # which is set in zeit.web.core.template.calculate_pagination
    dummy_request.GET['p'] = '8'
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/thema/test')
    view = zeit.web.site.view_centerpage.Centerpage(cp, dummy_request)
    assert view.next_page_url == 'http://example.com?p=9'


def test_prev_page_url_should_be_set_on_page_based_paginated_centerpages(
        application, dummy_request):

    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = ([{'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/01'}
                    for i in range(12)])

    dummy_request.GET['p'] = '2'
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/thema/test')
    view = zeit.web.site.view_centerpage.Centerpage(cp, dummy_request)
    assert view.prev_page_url == 'http://example.com'

    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = ([{'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/01'}
                    for i in range(22)])

    dummy_request.GET['p'] = '3'
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/thema/test')
    view = zeit.web.site.view_centerpage.Centerpage(cp, dummy_request)
    assert view.prev_page_url == 'http://example.com?p=2'


def test_next_page_url_should_be_set_on_date_based_paginated_centerpages(
        clock, application, dummy_request):

    clock.freeze(zeit.web.core.date.parse_date(
        '2016-05-10T1:23:59.780412+00:00'))

    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/news/index')
    view = zeit.web.site.view_centerpage.Centerpage(cp, dummy_request)
    assert view.next_page_url == 'http://example.com?date=2016-05-09'


def test_prev_page_url_should_be_set_on_date_based_paginated_centerpages(
        clock, application, dummy_request):

    clock.freeze(zeit.web.core.date.parse_date(
        '2016-05-10T1:23:59.780412+00:00'))

    dummy_request.GET['date'] = '2016-05-09'
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/news/index')
    view = zeit.web.site.view_centerpage.Centerpage(cp, dummy_request)
    assert view.prev_page_url == 'http://example.com'

    dummy_request.GET['date'] = '2016-05-08'
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/news/index')
    view = zeit.web.site.view_centerpage.Centerpage(cp, dummy_request)
    assert view.prev_page_url == 'http://example.com?date=2016-05-09'


def test_dynamic_centerpage_contains_webtrekk_pagenumber(
        application, dummy_request):

    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
        {'uniqueId': 'http://xml.zeit.de/artikel/01'} for i in range(22)]

    dummy_request.GET['p'] = '2'
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/thema/test')
    view = zeit.web.site.view_centerpage.Centerpage(cp, dummy_request)
    assert view.webtrekk['customParameter'].get('cp3') == '2/3'


def test_advertorial_cp_contains_correct_webtrekk_param(dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/advertorial-index')
    view = zeit.web.site.view_centerpage.Centerpage(context, dummy_request)
    assert view.webtrekk['customParameter']['cp26'] == 'centerpage.advertorial'


def test_materialized_series_cp_contains_correct_webtrekk_param(dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/serie/70-jahre-zeit')
    view = zeit.web.site.view_centerpage.Centerpage(context, dummy_request)
    assert view.webtrekk['customParameter'][
        'cp26'] == 'centerpage.ins_serienseite'


def test_dynamic_series_cp_contains_correct_webtrekk_param(dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/serie/alpha-centauri')
    view = zeit.web.site.view_centerpage.Centerpage(context, dummy_request)
    assert view.webtrekk['customParameter']['cp26'] == 'centerpage.serienseite'


def test_materialized_topic_cp_contains_correct_webtrekk_param(dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/thema/jurastudium')
    view = zeit.web.site.view_centerpage.Centerpage(context, dummy_request)
    assert view.webtrekk['customParameter']['cp26'] == 'centerpage.topicpage'


def test_dynamic_topic_cp_contains_correct_webtrekk_param(dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/thema/berlin')
    view = zeit.web.site.view_centerpage.Centerpage(context, dummy_request)
    assert view.webtrekk['customParameter'][
        'cp26'] == 'centerpage.keywordpage.location'


def test_invisible_region_should_not_be_rendered(application, testbrowser):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/invisible-teaser')
    xml = context.xml
    visible = len(xml.xpath('//cluster')) - len(xml.xpath(
        '//cluster[@visible="False"]'))
    browser = testbrowser('/zeit-online/invisible-teaser')
    assert len(browser.cssselect('.cp-region')) == visible


def test_invisible_area_should_not_be_rendered(application, testbrowser):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/invisible-teaser')
    xml = context.xml

    visible = len(
        xml.xpath('//cluster[@visible="True"]/region')) - len(
        xml.xpath('//region[@visible="False"]'))

    browser = testbrowser('/zeit-online/invisible-teaser')
    assert len(browser.cssselect('.cp-area')) == visible


def test_invisible_module_should_not_be_rendered(application, testbrowser):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/invisible-teaser')
    xml = context.xml
    path = '//cluster[@visible="True"]/region[@visible="True"]/container'
    visible = len(
        xml.xpath(path)) - len(
        xml.xpath('//container[@visible="False"]'))

    browser = testbrowser('/zeit-online/invisible-teaser')
    assert len(browser.cssselect('.cp-area > *')) == visible
