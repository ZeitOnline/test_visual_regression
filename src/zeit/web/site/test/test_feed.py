import requests
import lxml.etree
import zope.component
import zeit.solr.interfaces


def test_newsfeed_should_only_render_cp2015(testserver):
    res = requests.get(
        '%s/index' % testserver.url,
        headers={'Host': 'newsfeed.zeit.de'})

    assert res.status_code == 200

    res = requests.get(
        '%s/centerpage/index' % testserver.url,
        headers={'Host': 'newsfeed.zeit.de'})

    assert res.status_code == 404

    res = requests.get(
        '%s/artikel/01' % testserver.url,
        headers={'Host': 'newsfeed.zeit.de'})

    assert res.status_code == 404


def test_newsfeed_should_render_some_rss(testserver):
    res = requests.get(
        '%s/index' % testserver.url,
        headers={'Host': 'newsfeed.zeit.de'})

    xml = lxml.etree.fromstring(res.content)
    assert xml.tag == 'rss'


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
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId': 'http://xml.zeit.de/artikel/01'}]
    res = requests.get(
        '{}/autoren/author3'.format(testserver.url),
        headers={'Host': 'newsfeed.zeit.de'})

    xml = lxml.etree.fromstring(res.content)
    assert xml.xpath('//item/title/text()')[0].startswith(
        'Gentrifizierung: Mei, is des traurig!')
