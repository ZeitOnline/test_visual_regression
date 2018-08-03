import requests
import lxml.etree
import zope.component

import zeit.retresco.interfaces
import zeit.solr.interfaces

import zeit.web.site.view_feed


def test_newsfeed_should_render_magazin_and_campus(testserver):
    res = requests.get(
        '%s/zeit-magazin/index' % testserver.url,
        headers={'Host': 'newsfeed.zeit.de'})
    assert res.status_code == 200

    res = requests.get(
        '%s/campus/index' % testserver.url,
        headers={'Host': 'newsfeed.zeit.de'})
    assert res.status_code == 200


def test_newsfeed_should_render_some_rss(testserver):
    res = requests.get(
        '%s/index' % testserver.url,
        headers={'Host': 'newsfeed.zeit.de'})

    xml = lxml.etree.fromstring(res.content)
    assert xml.tag == 'rss'
    assert xml.find('channel').find('link').text == 'https://www.zeit.de/index'
    assert (
        xml.find('channel').find('image').find('link').text ==
        'https://www.zeit.de/index')


def test_newsfeed_should_render_some_rss_cp(testserver):
    res = requests.get(
        '%s/campus/feedindex' % testserver.url,
        headers={'Host': 'newsfeed.zeit.de'})

    xml = lxml.etree.fromstring(res.content)
    assert xml.tag == 'rss'
    assert (
        xml.find('channel').find('link').text ==
        'https://www.zeit.de/campus/feedindex')
    assert (
        xml.find('channel').find('image').find('link').text ==
        'https://www.zeit.de/campus/feedindex')


def test_newsfeed_should_have_custom_max_age_header(testserver):
    res = requests.get(
        '%s/index' % testserver.url,
        headers={'Host': 'newsfeed.zeit.de'})

    assert res.headers.get('Cache-Control') == 'max-age=25'


def test_newsfeed_should_concat_supertitle_and_title(testserver):
    res = requests.get(
        '%s/index' % testserver.url,
        headers={'Host': 'newsfeed.zeit.de'})

    xml = lxml.etree.fromstring(res.content)
    assert xml.xpath('//item/title/text()')[1].startswith('"Der Hobbit": Geht')


def test_newsfeed_should_render_an_authorfeed(testserver):
    es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    es.resolve_results = False
    es.results = [
        {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/01',
         'doc_type': 'article',
         'payload': {'body': {'title': 'Mei, is des traurig!'}}}
    ]
    res = requests.get(
        '{}/autoren/author3'.format(testserver.url),
        headers={'Host': 'newsfeed.zeit.de'})

    xml = lxml.etree.fromstring(res.content)
    assert xml.xpath('//item/title/text()')[0].startswith(
        'Mei, is des traurig!')


def test_socialflow_feed_contains_social_fields(testserver):
    feed_path = '/zeit-magazin/centerpage/index/rss-socialflow-twitter'
    res = requests.get(
        testserver.url + feed_path, headers={'Host': 'newsfeed.zeit.de'})

    assert res.status_code == 200
    assert res.headers['Content-Type'].startswith('application/rss+xml')
    feed = res.text
    assert '<atom:link href="http://newsfeed.zeit.de%s"' % feed_path in feed
    assert ('<link>https://www.zeit.de/zeit-magazin/'
            'centerpage/article_image_asset</link>' in feed)
    assert '<content:encoded>Twitter-Text' in feed
    assert '<content:encoded>Facebook-Text' not in feed

    feed_path = '/zeit-magazin/centerpage/index/rss-socialflow-facebook'
    res = requests.get(
        testserver.url + feed_path, headers={'Host': 'newsfeed.zeit.de'})
    feed = res.text
    assert '<content:encoded>Twitter-Text' not in feed
    assert '<content:encoded>Facebook-Text' in feed
    assert '<content:encoded>FB-ZMO' not in feed
    assert '<content:encoded>FB-ZCO' not in feed

    feed_path = '/zeit-magazin/centerpage/index/rss-socialflow-facebook-zmo'
    res = requests.get(
        testserver.url + feed_path, headers={'Host': 'newsfeed.zeit.de'})
    feed = res.text
    assert '<content:encoded>Twitter-Text' not in feed
    assert '<content:encoded>Facebook-Text' not in feed
    assert '<content:encoded>FB-ZMO' in feed
    assert '<content:encoded>FB-ZCO' not in feed

    feed_path = '/campus/centerpage/index/rss-socialflow-facebook'
    res = requests.get(
        testserver.url + feed_path, headers={'Host': 'newsfeed.zeit.de'})
    feed = res.text
    assert '<content:encoded>Twitter-Text' not in feed
    assert '<content:encoded>Facebook-Text' in feed
    assert '<content:encoded>FB-ZMO' not in feed
    assert '<content:encoded>FB-ZCO' not in feed

    feed_path = '/campus/centerpage/index/rss-socialflow-facebook-zco'
    res = requests.get(
        testserver.url + feed_path, headers={'Host': 'newsfeed.zeit.de'})
    feed = res.text
    assert '<content:encoded>Twitter-Text' not in feed
    assert '<content:encoded>Facebook-Text' not in feed
    assert '<content:encoded>FB-ZMO' not in feed
    assert '<content:encoded>FB-ZCO' in feed


def test_instant_article_feed_should_be_rendered(testserver):
    res = requests.get(
        '{}/zeit-magazin/centerpage/index/rss-instantarticle'
        .format(testserver.url),
        headers={'Host': 'newsfeed.zeit.de'})
    parser = lxml.etree.XMLParser(strip_cdata=False)
    xml = lxml.etree.fromstring(res.content, parser)
    source = xml.xpath('./channel/*[local-name()="include"]/@src')[0]

    # This is an URL from an esi include, which needs to have an http scheme,
    # even though we deliver www.zeit.de via https.
    assert source == ('http://www.zeit.de/'
                      'instantarticle-item/zeit-magazin/'
                      'centerpage/article_image_asset')


def test_roost_feed_contains_mobile_override_text(testserver,
                                                  preserve_settings):
    feed_path = '/zeit-magazin/centerpage/index/rss-roost'
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    settings['transform_to_secure_links_for'] = ''
    res = requests.get(
        testserver.url + feed_path, headers={'Host': 'newsfeed.zeit.de'})

    assert res.status_code == 200
    assert res.headers['Content-Type'].startswith('application/rss+xml')
    feed = res.text
    assert '<atom:link href="http://newsfeed.zeit.de%s"' % feed_path in feed
    assert ('<link>http://www.zeit.de/zeit-magazin/'
            'centerpage/article_image_asset</link>' in feed)
    assert '<title>Article Image Asset Sptzmarke</title>' in feed
    assert '<content:encoded>Mobile-Text' in feed


def test_queries_should_be_joined():
    url = 'http://www.zeit.de/mypath?myquery=foo'
    query = [('foo', 'baa'), ('batz', 'badumm')]
    assert zeit.web.site.view_feed.join_queries(url, query) == (
        'http://www.zeit.de/mypath?myquery=foo&foo=baa&batz=badumm')

    url = 'http://www.zeit.de/mypath'
    query = [('foo', 'baa'), ('batz', 'badumm')]
    assert zeit.web.site.view_feed.join_queries(url, query) == (
        'http://www.zeit.de/mypath?foo=baa&batz=badumm')


def test_yahoo_feed_is_only_available_from_newsfeed_host(testserver):
    feed_path = '/administratives/yahoofeed/rss-yahoo'
    res_newsfeed = requests.get(
        testserver.url + feed_path, headers={'Host': 'newsfeed.zeit.de'})
    assert res_newsfeed.status_code == 200

    res_www = requests.get(
        testserver.url + feed_path, headers={'Host': 'www.zeit.de'})
    assert res_www.status_code == 404


def test_yahoo_feed_is_only_available_for_specific_page(testserver):
    res = requests.get(
        testserver.url + '/administratives/yahoofeed/rss-yahoo',
        headers={'Host': 'newsfeed.zeit.de'})
    assert res.status_code == 200

    res = requests.get(
        testserver.url + '/index/rss-yahoo',
        headers={'Host': 'newsfeed.zeit.de'})
    assert res.status_code == 404


def test_yahoo_feed_contains_expected_fields(testserver):

    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/01',
         'type': 'article'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/02',
         'type': 'article'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/zeit',
         'type': 'article'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/simple',
         'type': 'article'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/tags',
         'type': 'article'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/fischer',
         'type': 'article'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/01',
         'type': 'article'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/02',
         'type': 'article'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/zeit',
         'type': 'article'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/simple',
         'type': 'article'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/tags',
         'type': 'article'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/fischer',
         'type': 'article'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/01',
         'type': 'article'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/02',
         'type': 'article'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/zeit',
         'type': 'article'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/simple',
         'type': 'article'},
    ]

    res = requests.get(
        testserver.url + '/administratives/yahoofeed/rss-yahoo',
        headers={'Host': 'newsfeed.zeit.de'})

    xml = lxml.etree.fromstring(res.content)
    assert len(xml.xpath('//item')) == 16
    assert len(xml.xpath('//title')) == 17

    assert len(xml.xpath('//item//description')) == 16
    assert len(xml.xpath('//item//pubDate')) == 16
    assert len(xml.xpath('//item//guid')) == 16
    assert len(xml.xpath('//item//category')) == 16

    # check if long articles are cut off
    assert res.content.count('Lesen Sie hier weiter!') == 4
    assert res.content.count('Nancy kennt sich.') == 1


def test_msn_feed_contains_expected_fields(testserver):

    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/01',
         'type': 'article',
         'title': 'Dummytitle'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/02',
         'type': 'article',
         'title': 'Dummytitle'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/zeit',
         'type': 'article',
         'title': 'Dummytitle'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/simple',
         'type': 'article',
         'title': 'Dummytitle'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/tags',
         'type': 'article',
         'title': 'Dummytitle'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/fischer',
         'type': 'article',
         'title': 'Dummytitle'}
    ]

    res = requests.get(
        testserver.url + '/administratives/msnfeed/rss-msn',
        headers={'Host': 'newsfeed.zeit.de'})

    xml = lxml.etree.fromstring(res.content)
    assert len(xml.xpath('//item')) > 0
    assert len(xml.xpath('//title')) > 0

    assert len(xml.xpath('//item//title')) > 0
    assert len(xml.xpath('//item//publishedDate')) > 0
    assert len(xml.xpath('//item//guid')) > 0
    assert len(xml.xpath('//item//webUrl')) > 0
    assert len(xml.xpath('//item//mi:dateTimeWritten', namespaces={
        'mi': 'http://schemas.ingestion.microsoft.com/common/'
    })) > 0
    assert len(xml.xpath('//item//content:encoded', namespaces={
        'content': 'http://purl.org/rss/1.0/modules/content/'
    })) > 0


def test_msn_feed_item_contains_copyright_information(testserver):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/01',
         'type': 'article',
         'title': 'Dummytitle'}
    ]

    res = requests.get(
        testserver.url + '/administratives/msnfeed/rss-msn',
        headers={'Host': 'newsfeed.zeit.de'})

    assert 'data-license-id="12345678"' in res.content
    assert 'data-portal-copyright="\xc2' in res.content
    assert ' Warner Bros."' in res.content
    assert 'data-licensor-name="dpa"' in res.content
