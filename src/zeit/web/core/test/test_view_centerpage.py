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


def test_gsitemap_overview_pagination(testbrowser):
    """total_pages is 2, look at count attribute in gsitemaps/index.xml"""
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId': 'http://xml.zeit.de/doc1'}]
    browser = testbrowser('/gsitemaps/index.xml')
    assert len(browser.document.xpath('//sitemapindex/sitemap')) == 1
    solr.results = [{'uniqueId': 'http://xml.zeit.de/doc1'},
                    {'uniqueId': 'http://xml.zeit.de/doc2'},
                    {'uniqueId': 'http://xml.zeit.de/doc3'}]
    browser = testbrowser('/gsitemaps/index.xml')
    assert len(browser.document.xpath('//sitemapindex/sitemap')) == 2
    solr.results = [{'uniqueId': 'http://xml.zeit.de/doc1'},
                    {'uniqueId': 'http://xml.zeit.de/doc2'},
                    {'uniqueId': 'http://xml.zeit.de/doc3'},
                    {'uniqueId': 'http://xml.zeit.de/doc4'}]
    browser = testbrowser('/gsitemaps/index.xml')
    assert len(browser.document.xpath('//sitemapindex/sitemap')) == 2
    solr.results = [{'uniqueId': 'http://xml.zeit.de/doc1'},
                    {'uniqueId': 'http://xml.zeit.de/doc2'},
                    {'uniqueId': 'http://xml.zeit.de/doc3'},
                    {'uniqueId': 'http://xml.zeit.de/doc4'},
                    {'uniqueId': 'http://xml.zeit.de/doc5'},
                    {'uniqueId': 'http://xml.zeit.de/doc6'},
                    {'uniqueId': 'http://xml.zeit.de/doc7'},
                    {'uniqueId': 'http://xml.zeit.de/doc8'},
                    {'uniqueId': 'http://xml.zeit.de/doc9'},
                    {'uniqueId': 'http://xml.zeit.de/doc10'},
                    {'uniqueId': 'http://xml.zeit.de/doc11'}]
    browser = testbrowser('/gsitemaps/index.xml')
    assert len(browser.document.xpath('//sitemapindex/sitemap')) == 6


def test_gsitemap_page_with_image_copyright(testbrowser):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{
        'image-base-id': ['http://xml.zeit.de/zeit-online/image/'
                          'filmstill-hobbit-schlacht-fuenf-hee/'],
        'uniqueId': 'http://xml.zeit.de/campus/article/01-countdown-studium'}]
    browser = testbrowser('/gsitemaps/index.xml?p=1')
    assert (browser.document.xpath('//url/loc')[0].text ==
            'http://localhost/campus/article/01-countdown-studium')
    assert (browser.document.xpath('//url/lastmod')[0].text ==
            '2016-02-18 13:50:52.380804+01:00')
    xml = lxml.etree.fromstring(browser.contents)
    ns = 'http://www.google.com/schemas/sitemap-image/1.1'
    assert xml.xpath('//image:image', namespaces={'image': ns})[0] is not None
    assert (
        xml.xpath(
            '//image:image/image:loc', namespaces={'image': ns})[0].text ==
        'http://localhost/zeit-online/image/'
        'filmstill-hobbit-schlacht-fuenf-hee/wide__1300x731')
    assert (
        xml.xpath(
            '//image:image/image:caption', namespaces={'image': ns})[0].text ==
        u'Handlung, wohin man auch schaut in dieser Szene aus dem letzten '
        u'Hobbit-Teil "Die Schlacht der fünf Heere" '
        u'(©\xa0Warner Bros.)')


def test_gsitemap_page_without_image(testbrowser, monkeypatch):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{
        'uniqueId': 'http://xml.zeit.de/zeit-online/article/'
        'article_with_broken_image_asset'}]
    browser = testbrowser('/gsitemaps/index.xml?p=1')
    assert (browser.document.xpath('//url/loc')[0].text ==
            'http://localhost/zeit-online/article/'
            'article_with_broken_image_asset')
    xml = lxml.etree.fromstring(browser.contents)
    ns = 'http://www.google.com/schemas/sitemap-image/1.1'
    assert not xml.xpath('//image:image', namespaces={'image': ns})


def test_gsitemap_newssite(testbrowser):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{
        'image-base-id': ['http://xml.zeit.de/zeit-online/image/'
                          'filmstill-hobbit-schlacht-fuenf-hee/'],
        'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/autorenbox'},
        {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/autorenbox'}]
    browser = testbrowser('/gsitemaps/newsitemap.xml')
    assert (browser.document.xpath('//url/loc')[0].text ==
            'http://localhost/zeit-magazin/article/autorenbox')
    assert (browser.document.xpath('//url/lastmod')[0].text ==
            '2014-04-29 13:00:55.287082+02:00')
    xml = lxml.etree.fromstring(browser.contents)
    ns = {'image': 'http://www.google.com/schemas/sitemap-image/1.1',
          'n': 'http://www.google.com/schemas/sitemap-news/0.9'}
    assert xml.xpath('//n:news', namespaces=ns)[0] is not None
    assert xml.xpath('//n:news/n:publication', namespaces=ns)[0] is not None
    assert (
        xml.xpath('//n:news/n:publication/n:name', namespaces=ns)[0].text ==
        'ZEIT ONLINE')
    assert (
        xml.xpath(
            '//n:news/n:publication/n:language', namespaces=ns)[0].text ==
        'de')
    assert (
        xml.xpath('//n:news/n:title', namespaces=ns)[0].text ==
        'Big Data: Schwanger ohne digitale Spuren')
    assert (
        xml.xpath('//n:news/n:keywords', namespaces=ns)[0].text ==
        u'Schwangerschaft, Konsumverhalten, Werbung, Tracking, Facebook, '
        u'Behörde, Minnesota, USA, New York, Digital, Datenschutz')
    assert xml.xpath('//image:image', namespaces=ns)[0] is not None
    assert (
        xml.xpath(
            '//image:image/image:loc', namespaces=ns)[0].text ==
        'http://localhost/zeit-online/image/'
        'filmstill-hobbit-schlacht-fuenf-hee/wide__1300x731')
    assert (
        xml.xpath(
            '//image:image/image:caption', namespaces=ns)[0].text ==
        u'Handlung, wohin man auch schaut in dieser Szene aus dem letzten '
        u'Hobbit-Teil "Die Schlacht der fünf Heere" '
        u'(©\xa0Warner Bros.)')
    assert len(xml.xpath('//image:image', namespaces=ns)) == 1


def test_gsitemap_video(testbrowser):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{
        'uniqueId': 'http://xml.zeit.de/video/2014-01/1953013471001'
    }]
    browser = testbrowser('/gsitemaps/video.xml?p=1')
    assert (browser.document.xpath('//url/loc')[0].text ==
            'http://localhost/video/2014-01/1953013471001')
    xml = lxml.etree.fromstring(browser.contents)
    ns = {'video': 'http://www.google.com/schemas/sitemap-video/1.1'}
    assert xml.xpath('//video:video', namespaces=ns)[0] is not None
    assert (
        xml.xpath('//video:thumbnail_loc', namespaces=ns)[0].text ==
        'http://brightcove.vo.llnwd.net/d21/unsecured/media/18140073001/'
        '18140073001_1956041162001_ari-origin05-arc-154-1352391648628.jpg?'
        'pubId=18140073001')
    assert (
        xml.xpath('//video:content_loc', namespaces=ns)[0].text ==
        'http://brightcove.vo.llnwd.net/pd16/media/18140073001/'
        '18140073001_1953016536001_fotomomente-nordlichter.mp4')
    assert (
        xml.xpath('//video:title', namespaces=ns)[0].text ==
        u'Foto-Momente: Die stille Schönheit der Polarlichter')
    assert (
        xml.xpath('//video:description', namespaces=ns)[0].text.strip() ==
        'Sie sind eines der faszinierendsten Schauspiele, die die Natur zu '
        'bieten hat: Polarlichter, auch als Aurora borealis bekannt, '
        'illuminieren den Himmel in atemberaubenden Farben.')
    assert (
        xml.xpath('//video:publication_date', namespaces=ns)[0].text.strip() ==
        '2012-11-08 11:37:55+01:00')
    assert (
        xml.xpath('//video:category', namespaces=ns)[0].text.strip() ==
        'Wissen')
    assert (
        xml.xpath('//video:family_friendly', namespaces=ns)[0].text.strip() ==
        'yes')


def test_gsitemap_themen_overview(testbrowser):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{
        'uniqueId': 'http://xml.zeit.de/campus/article/01-countdown-studium'}]
    browser = testbrowser('/gsitemaps/themenindex.xml')
    assert browser.document.xpath('//sitemapindex')[0] is not None
    assert (
        browser.document.xpath('//sitemapindex/sitemap/loc')[5].text ==
        'http://www.zeit.de/gsitemaps/themenindex.xml?p=6')


def test_gsitemap_themen_page(testbrowser):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{
        'uniqueId': 'http://xml.zeit.de/campus/article/01-countdown-studium'}]
    browser = testbrowser('/gsitemaps/themenindex.xml?p=5')
    assert len(browser.document.xpath('//url')) == 100
    assert (
        browser.document.xpath('//url/loc')[1].text ==
        'http://www.zeit.de/thema/guenter-grass')


def test_gsitemap_themen_last_page(testbrowser):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{
        'uniqueId': 'http://xml.zeit.de/campus/article/01-countdown-studium'}]
    browser = testbrowser('/gsitemaps/themenindex.xml?p=138')
    assert len(browser.document.xpath('//url')) == 54
    assert (
        browser.document.xpath('//url/loc')[5].text ==
        'http://www.zeit.de/thema/kenenisa-bekele')


def test_gsitemap_appcon(monkeypatch, testbrowser):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
        {'uniqueId': 'http://xml.zeit.de/campus/article/01-countdown-studium'},
        {'uniqueId': 'http://blog.zeit.de/blogs/nsu-blog-bouffier'}]
    monkeypatch.setattr(zeit.web.core.interfaces, 'IImage', None)
    browser = testbrowser('/gsitemaps/appconsitemap.xml?p=1')
    assert (
        browser.document.xpath('//url/loc')[0].text ==
        'http://localhost/campus/article/01-countdown-studium')
    xml = lxml.etree.fromstring(browser.contents)
    ns = {'xhtml': 'http://www.w3.org/1999/xhtml'}
    assert (
        xml.xpath('//xhtml:link/@href', namespaces=ns)[0] ==
        'android-app://de.zeit.online/http/localhost/campus/'
        'article/01-countdown-studium')
    assert (
        xml.xpath('//xhtml:link/@href', namespaces=ns)[1] ==
        'android-app://de.zeit.online/http/blog.zeit.de/blogs/'
        'nsu-blog-bouffier')
