import pytest
import requests


@pytest.fixture(params=['www', 'scripts', 'static'])
def hostname(request):
    yield request.param


def test_renders_text_content(testserver, hostname):
    r = requests.get(
        '%s/text/dummy' % testserver.url,
        headers={'Host': hostname + '.zeit.de'})
    assert r.status_code == 200
    assert r.headers['content-type'] == 'text/plain; charset=UTF-8'
    assert r.headers['Access-Control-Allow-Origin'] == '*'
    assert r.content == 'zeit.web\n'


def test_renders_xml_content(testserver, hostname):
    r = requests.get(
        '%s/config/community_maintenance.xml' % testserver.url,
        headers={'Host': hostname + '.zeit.de'})
    assert r.status_code == 200
    # As of libmagic 5.30 our meta files are recognised as text/xml (ND)
    assert r.headers['content-type'] in (
        'application/xml; charset=UTF-8', 'text/xml; charset=UTF-8')
    assert r.headers['Access-Control-Allow-Origin'] == '*'
    assert 'maintenance' in r.content


def test_renders_unknown_content(testserver, hostname):
    r = requests.get(
        '%s/text/dummy' % testserver.url,
        headers={'Host': hostname + '.zeit.de'})
    assert r.status_code == 200
    assert r.headers['content-type'] == 'text/plain; charset=UTF-8'
    assert r.headers['Access-Control-Allow-Origin'] == '*'
    assert r.content == 'zeit.web\n'


def test_renders_unknown_text_content_with_mime_type(testserver, hostname):
    r = requests.get(
        '%s/davcontent/raw.css' % testserver.url,
        headers={'Host': hostname + '.zeit.de'})
    assert r.status_code == 200
    assert r.headers['content-type'] == 'text/css; charset=UTF-8'
    assert r.headers['Access-Control-Allow-Origin'] == '*'
    assert 'extraDivFromHell' in r.content


def test_renders_rss_feeds(testserver, hostname):
    r = requests.get(
        '%s/davcontent/feed.rss' % testserver.url,
        headers={'Host': hostname + '.zeit.de'})
    assert r.status_code == 200
    # As of libmagic 5.30 our meta files are recognised as text/xml (ND)
    assert r.headers['content-type'] in (
        'application/xml; charset=UTF-8', 'text/xml; charset=UTF-8')
    assert r.headers['Access-Control-Allow-Origin'] == '*'
    assert 'heise online' in r.content


def test_renders_meta_files(testserver, hostname):
    r = requests.get(
        '%s/text/dummy.meta' % testserver.url,
        headers={'Host': hostname + '.zeit.de'})
    assert r.status_code == 200
    # As of libmagic 5.30 our meta files are recognised as text/xml (ND)
    assert r.headers['content-type'] in (
        'application/xml; charset=UTF-8', 'text/xml; charset=UTF-8')
    assert r.headers['Access-Control-Allow-Origin'] == '*'
    assert 'robots.txt' in r.content


@pytest.mark.parametrize('statichost', ['static', 'scripts'])
def test_cannot_access_content_on_static_hosts(testserver, statichost):
    r = requests.get('%s/zeit-online/index' % testserver.url,
                     headers={'Host': statichost + '.zeit.de'},
                     timeout=3600)
    assert r.status_code == 404
    r = requests.get('%s/zeit-online/image/weltall/original' % testserver.url,
                     headers={'Host': statichost + '.zeit.de'})
    assert r.status_code == 404


def test_renders_raw_files_with_their_contenttype(testserver):
    r = requests.get(
        '%s/davcontent/example.css' % testserver.url,
        headers={'Host': 'www.zeit.de'})
    assert r.status_code == 200
    assert r.headers['content-type'] == 'text/css; charset=UTF-8'
    assert r.headers['Access-Control-Allow-Origin'] == '*'
    assert 'koennseMalEbenWrapper' in r.content


def test_adds_cache_headers_to_raw_files(testserver):
    r = requests.get(
        '%s/davcontent/example.css' % testserver.url,
        headers={'Host': 'www.zeit.de'})
    assert r.headers['Cache-control'] == 'max-age=3600'
