# -*- coding: utf-8 -*-
import lxml.etree
import magic
import mock
import os
import requests
import sys
import zeit.web.core


def test_xml_renders_with_host_header(testserver):
    res = requests.get(
        '%s/zeit-online/index' % testserver.url,
        headers={'Host': 'xml.zeit.de'})
    assert res.status_code == 200

    res = requests.get(
        '%s/zeit-magazin/centerpage/index' % testserver.url,
        headers={'Host': 'xml.zeit.de'})
    assert res.status_code == 200


def test_xml_renders_with_route_name(testserver):
    res = requests.get(
        '%s/xml/zeit-online/index' % testserver.url)
    assert res.status_code == 200

    res = requests.get(
        '%s/xml/zeit-magazin/centerpage/index' % testserver.url)
    assert res.status_code == 200


def test_xml_renders_iso_8859_1(testserver):
    path = os.path.dirname(
        zeit.web.core.__file__) + '/data/zeit-online/article/01'
    with open(path) as f:
        blob = f.read()
        f.close
    m = magic.Magic(flags=magic.MAGIC_MIME_ENCODING)
    encoding = m.id_buffer(blob)
    assert encoding == 'utf-8'
    res = requests.get(
        '%s/zeit-online/article/01' % testserver.url,
        headers={'Host': 'xml.zeit.de'})
    assert res.encoding == 'iso-8859-1'


def test_xml_renders_unicode_as_codepoints(testserver):
    res = requests.get(
        '%s/zeit-magazin/article/03' % testserver.url,
        headers={'Host': 'xml.zeit.de'})
    assert (
        '<title>Aus dem Keller des \xc9lys\xe9epalasts</title>' in res.content)


def test_xml_renders_article_as_expected(testserver):
    res = requests.get(
        '%s/zeit-online/article/01' % testserver.url,
        headers={'Host': 'xml.zeit.de'})

    doc = {
        'uuid': '{urn:uuid:9e7bf051-2299-43e4-b5e6-1fa81d097dbd}',
        'title': u'Geht\'s noch größer? ',
    }

    xml = lxml.etree.fromstring(res.content)
    assert xml.xpath('//attribute[@name="uuid"]')[0].text == doc['uuid']
    assert xml.xpath('//body/title')[0].text == doc['title']


def test_xml_renders_article_with_xml_content_view(testserver):
    with mock.patch('zeit.web.core.view_xml.XMLContent.__call__') as view:
        requests.get(
            '%s/zeit-online/article/01' % testserver.url,
            headers={'Host': 'xml.zeit.de'})
    assert view.called


def test_xml_renders_column_articles(testserver):
    res = requests.get(
        '%s/zeit-online/article/fischer' % testserver.url,
        headers={'Host': 'xml.zeit.de'})
    assert res.status_code == 200


def test_xml_renders_centerpage_as_expected(testserver):
    res = requests.get(
        '%s/zeit-magazin/centerpage/index' % testserver.url,
        headers={'Host': 'xml.zeit.de'})

    doc = {
        'uuid': '{urn:uuid:55b36707-1d57-42e9-8e23-1aded6280e9f}',
        'title': 'Article Image Asset Titel',
    }

    xml = lxml.etree.fromstring(res.content)
    assert xml.xpath('//attribute[@name="uuid"]')[0].text == doc['uuid']
    assert xml.xpath('//block/title')[0].text == doc['title']


def test_xml_renders_centerpage_with_centerpage_view(testserver):
    with mock.patch('zeit.web.core.view_xml.Centerpage.__call__') as view:
        requests.get(
            '%s/zeit-magazin/centerpage/index' % testserver.url,
            headers={'Host': 'xml.zeit.de'})
    assert view.called


def test_xml_renders_videos(testserver):
    res = requests.get(
        '%s/video/2014-01/3089721834001' % testserver.url,
        headers={'Host': 'xml.zeit.de'})
    assert res.status_code == 200


def test_xml_renders_galleries(testserver):
    res = requests.get(
        '%s/galerien/bg-automesse-detroit-2014-usa' % testserver.url,
        headers={'Host': 'xml.zeit.de'})
    assert res.status_code == 200


def test_xml_renders_authors(testserver):
    res = requests.get(
        '%s/autoren/j_random' % testserver.url,
        headers={'Host': 'xml.zeit.de'})
    assert res.status_code == 200


def test_xml_renders_links(testserver):
    res = requests.get(
        '%s/zeit-online/link-object' % testserver.url,
        headers={'Host': 'xml.zeit.de'})
    assert res.status_code == 200


def test_xml_renders_article_with_meta_robots(testserver):
    res = requests.get(
        '%s/zeit-online/article/01' % testserver.url,
        headers={'Host': 'xml.zeit.de'})

    doc = {
        'html_meta_robots': 'index,follow,noodp,noydir,noarchive',
        'html_meta_robots_namespace':
            'http://namespaces.zeit.de/CMS/meta',
    }

    xml = lxml.etree.fromstring(res.content)
    assert (xml.xpath('//attribute[@name="html-meta-robots"]')[0].text ==
            doc['html_meta_robots'])
    assert (xml.xpath('//attribute[@name="html-meta-robots"]/@ns')[0] ==
            doc['html_meta_robots_namespace'])


def test_xml_renders_centerpage_with_mobile_alternative(testserver):
    res = requests.get(
        '%s/angebote/leseperlen' % testserver.url,
        headers={'Host': 'xml.zeit.de'})

    assert 'x-mobilealternative' in res.headers.keys()
    assert (res.headers['x-mobilealternative'] ==
            'http://marktplatz.zeit.de/advertorial/buchtipp/index')


def test_xml_renders_image(testserver):
    res = requests.get(
        '%s/davcontent/bild.jpg' % testserver.url,
        headers={'Host': 'xml.zeit.de'})

    assert res.headers['content-type'] == 'image/jpeg'
    assert 203640 == sys.getsizeof(res.content)


def test_xml_renders_text(testserver):
    res = requests.get(
        '%s/davcontent/text' % testserver.url,
        headers={'Host': 'xml.zeit.de'})

    assert res.headers['content-type'] == 'text/plain; charset=UTF-8'
    assert 'Global Drug Survey 2016' in res.content


def test_xml_renders_non_xml_content_view(testserver):
    with mock.patch('zeit.web.core.view_xml.NonXMLContent.__call__') as view:
        requests.get(
            '%s/davcontent/text' % testserver.url,
            headers={'Host': 'xml.zeit.de'})
    assert view.called


def test_xml_infobox_include(testserver):
    res = requests.get(
        '%s/campus/article/infobox' % testserver.url,
        headers={'Host': 'xml.zeit.de'})
    xml = lxml.etree.fromstring(res.content)
    assert (xml.xpath('//infobox')[0].get('href') ==
            'http://xml.zeit.de/zeit-online/article/info-bonobo')
    assert (xml.xpath('//infobox')[0].get('expires') ==
            '2016-08-28T14:00:24+00:00')
    assert (xml.xpath('//infobox')[0].get('publication-date') ==
            '2016-07-28T14:05:26+00:00')
    assert (xml.xpath('//infobox/container/supertitle')[0].text ==
            '10 Saurier sind super')


def test_xml_liveblog_include(testserver):
    res = requests.get(
        '%s/zeit-online/liveblog/champions-league' % testserver.url,
        headers={'host': 'xml.zeit.de'})
    xml = lxml.etree.fromstring(res.content)
    assert xml.xpath('//div[@data-type="esi-content"]')
    assert xml.xpath('//*[name()="esi:include"]')


def test_xml_adds_cors_header(testserver):
    res = requests.get(
        '%s/zeit-online/link-object' % testserver.url,
        headers={'Host': 'xml.zeit.de'})
    assert res.headers['Access-Control-Allow-Origin'] == '*'
    res = requests.get(
        '%s/davcontent/text' % testserver.url,
        headers={'Host': 'xml.zeit.de'})
    assert res.headers['Access-Control-Allow-Origin'] == '*'
