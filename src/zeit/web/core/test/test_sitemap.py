# coding: utf-8
import datetime
import urllib2

import mock
import pytest
import pytz
import lxml.etree
import zope.component

from zeit.cms.checkout.helper import checked_out
import zeit.content.article.testing
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.retresco.interfaces


def convert_results(result):
    content = zeit.cms.interfaces.ICMSContent(result['uniqueId'])
    converter = zeit.retresco.interfaces.ITMSRepresentation(content)
    return converter()


def set_results(results):
    es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    es.results = map(convert_results, results)


def test_gsitemap_index_ranking_pagination(testbrowser, workingcopy):
    """total_pages is 2, look at count attribute in gsitemaps/index.xml"""
    with checked_out(zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/gsitemaps/index.xml')) as co:
        area = co.body.values()[0].values()[0]
        area.kind = 'ranking'

    set_results([{'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/01'}])
    browser = testbrowser('/gsitemaps/index.xml')
    assert len(browser.document.xpath('//sitemapindex/sitemap')) == 1
    set_results([{'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/01'},
                 {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/02'},
                 {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/03'}])
    browser = testbrowser('/gsitemaps/index.xml')
    assert len(browser.document.xpath('//sitemapindex/sitemap')) == 2
    set_results([{'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/01'},
                 {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/02'},
                 {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/03'},
                 {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/04'}])
    browser = testbrowser('/gsitemaps/index.xml')
    assert len(browser.document.xpath('//sitemapindex/sitemap')) == 2
    set_results([{'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/01'},
                 {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/02'},
                 {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/03'},
                 {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/03a'},
                 {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/04'},
                 {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/05'},
                 {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/06'},
                 {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/07'},
                 {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/08'},
                 {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/09'},
                 {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/10'}])
    browser = testbrowser('/gsitemaps/index.xml')
    assert len(browser.document.xpath('//sitemapindex/sitemap')) == 6


def test_gsitemap_index_overview_stops_at_current_date(testbrowser, clock):
    clock.freeze(datetime.datetime(1946, 1, 10))
    browser = testbrowser('/gsitemaps/index.xml')
    links = browser.document.xpath('//sitemapindex/sitemap/loc')
    assert len(links) == 10
    assert (links[0].text ==
            'http://localhost/gsitemaps/index.xml?date=1946-01-01')


def test_gsitemap_page_with_image_copyright(testbrowser):
    set_results([{
        'uniqueId': 'http://xml.zeit.de/zeit-online/article/01'}])
    browser = testbrowser('/gsitemaps/index.xml?date=2000-01-01')
    assert (browser.document.xpath('//url/loc')[0].text ==
            'http://localhost/zeit-online/article/01')
    assert (browser.document.xpath('//url/lastmod')[0].text ==
            '2015-05-27T19:11:30+02:00')
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
        u'(©\xa0Warner Bros./dpa)')


def test_gsitemap_page_without_image(testbrowser, monkeypatch, workingcopy):
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    repository['article'] = zeit.content.article.testing.create_article()
    set_results([{
        'uniqueId': 'http://xml.zeit.de/article'}])
    browser = testbrowser('/gsitemaps/index.xml?date=2000-01-01')
    assert (browser.document.xpath('//url/loc')[0].text ==
            'http://localhost/article')
    xml = lxml.etree.fromstring(browser.contents)
    ns = 'http://www.google.com/schemas/sitemap-image/1.1'
    assert not xml.xpath('//image:image', namespaces={'image': ns})


def test_gsitemap_page_does_not_break_without_image_caption(
        testbrowser, monkeypatch):
    set_results([{
        'uniqueId': 'http://xml.zeit.de/zeit-online/article/01'}])
    monkeypatch.setattr(zeit.web.core.image.Image, 'caption', None)
    browser = testbrowser('/gsitemaps/index.xml?date=2000-01-01')
    xml = lxml.etree.fromstring(browser.contents)
    ns = 'http://www.google.com/schemas/sitemap-image/1.1'
    assert (
        xml.xpath(
            '//image:image/image:caption', namespaces={'image': ns})[0].text ==
        u'(©\xa0Warner Bros./dpa)')


def test_gsitemap_rejects_invalid_page_parameter(testbrowser):
    with pytest.raises(urllib2.HTTPError) as err:
        testbrowser('/gsitemaps/themenindex.xml?p=invalid')
    assert err.value.getcode() == 404


def test_gsitemap_page_does_not_contain_invalid_lastmod_date(
        testbrowser, monkeypatch):
    set_results([{
        'uniqueId': 'http://xml.zeit.de/campus/article/01-countdown-studium'}])
    monkeypatch.setattr(
        zeit.content.article.article.ArticleWorkflow, 'date_first_released',
        datetime.datetime(1967, 1, 1, 12, 50, 52, 380804, tzinfo=pytz.UTC))
    browser = testbrowser('/gsitemaps/index.xml?date=2000-01-01')
    assert (browser.document.xpath('//url/loc')[0].text ==
            'http://localhost/campus/article/01-countdown-studium')
    assert not browser.document.xpath('//url/lastmod')


def test_gsitemap_newssite(testbrowser):
    set_results([{
        'image-base-id': ['http://xml.zeit.de/zeit-online/image/'
                          'crystal-meth-nancy-schmidt/'],
        'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/autorenbox',
        'supertitle': 'Big Data',
        'title': 'Schwanger ohne digitale Spuren',
        'ressort': 'Digital',
        'sub_ressort': 'Datenschutz',
        'keyword': ['Schwangerschaft', 'Konsumverhalten'],
        'keyword_id': ['schwangerschaft', 'konsumverhalten']},
    ])
    browser = testbrowser('/gsitemaps/newsitemap.xml')
    assert (browser.document.xpath('//url/loc')[0].text ==
            'http://localhost/zeit-magazin/article/autorenbox')
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
        xml.xpath(
            '//n:news/n:publication_date',
            namespaces=ns)[0].text == '2014-04-29T13:00:55+02:00')
    assert (
        xml.xpath('//n:news/n:title', namespaces=ns)[0].text ==
        'Big Data: Schwanger ohne digitale Spuren')
    assert (
        xml.xpath('//n:news/n:keywords', namespaces=ns)[0].text ==
        u'Schwangerschaft, Konsumverhalten, Digital, Datenschutz')
    assert xml.xpath('//image:image', namespaces=ns)[0] is not None
    assert (
        xml.xpath(
            '//image:image/image:loc', namespaces=ns)[0].text ==
        'http://localhost/zeit-online/image/'
        'crystal-meth-nancy-schmidt/wide__1300x731')
    assert (
        xml.xpath(
            '//image:image/image:caption', namespaces=ns)[0].text ==
        u'Nancy Schmidt auf einem Feld in ihrem Heimatort zwischen '
        u'Gera und Jena (©\xa0Milos Djuric)')
    assert (
        xml.xpath(
            '//image:image/image:license', namespaces=ns)[0].text ==
        'http://www.milosdjuric.com/')


def test_gsitemap_news_does_not_contain_none_in_keywords(
        testbrowser, monkeypatch):
    set_results([{
        'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/autorenbox',
        'ressort': 'Digital',
        'keyword': ['Schwangerschaft', 'Konsumverhalten'],
        'keyword_id': ['schwangerschaft', 'konsumverhalten']},
    ])
    # sub_ressort is added as keyword as well, set it to None here to check if
    # 'None' is added keyword list
    monkeypatch.setattr(
        zeit.content.article.article.Article, 'sub_ressort', None
    )
    browser = testbrowser('/gsitemaps/newsitemap.xml')
    xml = lxml.etree.fromstring(browser.contents)
    ns = {'n': 'http://www.google.com/schemas/sitemap-news/0.9'}
    assert (
        xml.xpath('//n:news/n:keywords', namespaces=ns)[0].text ==
        u'Schwangerschaft, Konsumverhalten, Digital')


def test_gsitemap_video(testbrowser):
    set_results([{
        'uniqueId': 'http://xml.zeit.de/video/2014-01/1953013471001',
        'title': u'Foto-Momente: Die stille Schönheit der Polarlichter',
        'subtitle': 'Sie sind eines der faszinierendsten Schauspiele, die '
        'die Natur zu bieten hat: Polarlichter, auch als Aurora borealis '
        'bekannt, illuminieren den Himmel in atemberaubenden Farben.',
        'ressort': 'Wissen'
    }])
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    settings['image_prefix'] = 'http://img.example.com'
    browser = testbrowser('/gsitemaps/video.xml?date=2000-01-01')
    assert (browser.document.xpath('//url/loc')[0].text ==
            'http://localhost/video/2014-01/1953013471001')
    xml = lxml.etree.fromstring(browser.contents)
    ns = {'video': 'http://www.google.com/schemas/sitemap-video/1.1'}
    assert xml.xpath('//video:video', namespaces=ns)[0] is not None
    assert (u'http://img.example.com/video/2014-01/1953013471001/image_group/'
            u'thumbnail.jpg' ==
            xml.xpath('//video:thumbnail_loc', namespaces=ns)[0].text)
    assert (
        xml.xpath('//video:player_loc', namespaces=ns)[0].text ==
        u'https://players.brightcove.net/18140073001/SJENxUNKe_default'
        u'/index.html?videoId=1953013471001')
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
        '2012-11-08T11:37:55+01:00')
    assert (
        xml.xpath('//video:category', namespaces=ns)[0].text.strip() ==
        'Wissen')
    assert (
        xml.xpath('//video:family_friendly', namespaces=ns)[0].text.strip() ==
        'yes')


def test_gsitemap_video_creates_no_publication_date_field_if_no_date_is_set(
        testbrowser, monkeypatch):
    set_results([{
        'uniqueId': 'http://xml.zeit.de/video/2014-01/1953013471001'
    }])
    monkeypatch.setattr(
        zeit.workflow.asset.AssetWorkflow,
        'date_last_published_semantic', None)
    monkeypatch.setattr(
        zeit.workflow.asset.AssetWorkflow, 'date_first_released', None)
    browser = testbrowser('/gsitemaps/video.xml?date=2000-01-01')
    xml = lxml.etree.fromstring(browser.contents)
    ns = {'video': 'http://www.google.com/schemas/sitemap-video/1.1'}
    assert xml.xpath('//video:video', namespaces=ns)[0] is not None
    assert xml.xpath('//video:publication_date', namespaces=ns) == []


def test_gsitemap_video_does_not_call_bc_api(testbrowser, monkeypatch):
    import zeit.brightcove.connection
    set_results([{
        'uniqueId': 'http://xml.zeit.de/video/2014-01/1953013471001'
    }])
    mocked_get_video = mock.Mock()
    mocked_get_video.return_value = {
        'renditions': (),
        'thumbnail': None,
        'video_still': None,
    }
    monkeypatch.setattr(
        zeit.brightcove.connection.PlaybackAPI, 'get_video', mocked_get_video)
    testbrowser('/gsitemaps/video.xml?date=2000-01-01')
    assert not mocked_get_video.called, \
        'get_video from BC-API was called and should not have been'


def test_gsitemap_themen_overview(testbrowser, data_tms):
    browser = testbrowser('/gsitemaps/themenindex.xml')
    assert browser.document.xpath('//sitemapindex')[0] is not None
    assert (
        browser.document.xpath('//sitemapindex/sitemap/loc')[5].text ==
        'http://localhost/gsitemaps/themenindex.xml?p=6')


def test_gsitemap_themen_page(testbrowser, data_tms):
    browser = testbrowser('/gsitemaps/themenindex.xml?p=5')
    assert len(browser.document.xpath('//url')) == 10
    assert (
        browser.document.xpath('//url/loc')[1].text ==
        'http://localhost/thema/addis-abeba')


def test_gsitemap_themen_last_page(testbrowser, data_tms):
    browser = testbrowser('/gsitemaps/themenindex.xml?p=495')
    assert len(browser.document.xpath('//url')) == 7
    assert (
        browser.document.xpath('//url/loc')[-1].text ==
        'http://localhost/thema/sanliurfa')


def test_gsitemap_appcon(monkeypatch, testbrowser):
    set_results([
        {'uniqueId': 'http://xml.zeit.de/campus/article/01-countdown-studium'},
        {'uniqueId': 'http://blog.zeit.de/blogs/nsu-blog-bouffier'}
    ])
    monkeypatch.setattr(zeit.web.core.interfaces, 'IImage', None)
    browser = testbrowser('/gsitemaps/appconsitemap.xml?date=2000-01-01')
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
        'android-app://de.zeit.online/https/blog.zeit.de/blogs/'
        'nsu-blog-bouffier')


def test_gsitemap_appcon_creates_https_urls(monkeypatch, testbrowser):
    set_results([
        {'uniqueId': 'http://xml.zeit.de/campus/article/01-countdown-studium'},
        {'uniqueId': 'http://blog.zeit.de/blogs/nsu-blog-bouffier'}
    ])
    zeit.web.core.application.FEATURE_TOGGLES.set('https')
    monkeypatch.setattr(zeit.web.core.interfaces, 'IImage', None)
    browser = testbrowser('/gsitemaps/appconsitemap.xml?date=2000-01-01')
    xml = lxml.etree.fromstring(browser.contents)
    ns = {'xhtml': 'http://www.w3.org/1999/xhtml'}
    assert (
        browser.document.xpath('//url/loc')[0].text ==
        'https://localhost/campus/article/01-countdown-studium')
    assert (
        xml.xpath('//xhtml:link/@href', namespaces=ns)[0] ==
        'android-app://de.zeit.online/https/localhost/campus/'
        'article/01-countdown-studium')
    # Whats wrong with blogs?
    # Well, both should be transformed
    assert (
        browser.document.xpath('//url/loc')[1].text ==
        'https://blog.zeit.de/blogs/nsu-blog-bouffier')
    assert (
        xml.xpath('//xhtml:link/@href', namespaces=ns)[1] ==
        'android-app://de.zeit.online/https/blog.zeit.de/blogs/'
        'nsu-blog-bouffier')


def test_gsitemap_solr_uses_different_timeout_than_normal_solr(testbrowser):
    # use global sitemanager, it might have been manipulated before
    zope.component.hooks.setSite()
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    old_timeout = solr.timeout
    testbrowser('/gsitemaps/appconsitemap.xml?date=2000-01-01')
    sitemap_solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    assert sitemap_solr.timeout != old_timeout
    # request some random url which is not a sitemap
    testbrowser('/zeit-online/article/portraitbox_inline')
    newer_solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    assert newer_solr.timeout == old_timeout


def test_sitemaps_support_link_objects(testbrowser):
    set_results([{
        'uniqueId': 'http://xml.zeit.de/mylink',
        'doc_type': 'link',
        'url': 'http://example.com/link'
    }])
    browser = testbrowser('/gsitemaps/index.xml?date=2000-01-01')
    assert (browser.document.xpath('//url/loc')[0].text ==
            'http://example.com/link')


def test_sitemaps_treat_blogpost_as_link(testbrowser):
    set_results([{
        'uniqueId': 'http://blog.zeit.de/meinblog/foo',
        'doc_type': 'blogpost',
    }])
    browser = testbrowser('/gsitemaps/index.xml?date=2000-01-01')
    assert (browser.document.xpath('//url/loc')[0].text ==
            'https://blog.zeit.de/meinblog/foo')
