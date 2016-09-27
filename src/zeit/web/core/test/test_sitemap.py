# coding: utf-8
import lxml.etree
import zope.component

import zeit.solr.interfaces


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
                          'crystal-meth-nancy-schmidt/'],
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


def test_gsitemap_page_does_not_break_without_image_caption(
        testbrowser, monkeypatch):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{
        'image-base-id': ['http://xml.zeit.de/zeit-online/image/'
                          'filmstill-hobbit-schlacht-fuenf-hee/'],
        'uniqueId': 'http://xml.zeit.de/campus/article/01-countdown-studium'}]
    monkeypatch.setattr(zeit.web.core.image.Image, 'caption', None)
    browser = testbrowser('/gsitemaps/index.xml?p=1')
    print browser.contents
    xml = lxml.etree.fromstring(browser.contents)
    ns = 'http://www.google.com/schemas/sitemap-image/1.1'
    assert (
        xml.xpath(
            '//image:image/image:caption', namespaces={'image': ns})[0].text ==
        u'(©\xa0Warner Bros.)')


def test_gsitemap_newssite(testbrowser):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{
        'image-base-id': ['http://xml.zeit.de/zeit-online/image/'
                          'crystal-meth-nancy-schmidt/'],
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
    browser = testbrowser('/gsitemaps/themenindex.xml')
    assert browser.document.xpath('//sitemapindex')[0] is not None
    assert (
        browser.document.xpath('//sitemapindex/sitemap/loc')[5].text ==
        'http://localhost/gsitemaps/themenindex.xml?p=6')


def test_gsitemap_themen_page(testbrowser):
    browser = testbrowser('/gsitemaps/themenindex.xml?p=5')
    assert len(browser.document.xpath('//url')) == 10
    assert (
        browser.document.xpath('//url/loc')[1].text ==
        'http://localhost/thema/abschreibung')


def test_gsitemap_themen_last_page(testbrowser):
    browser = testbrowser('/gsitemaps/themenindex.xml?p=1376')
    assert len(browser.document.xpath('//url')) == 4
    assert (
        browser.document.xpath('//url/loc')[3].text ==
        'http://localhost/thema/2.-fussball-bundesliga')


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
