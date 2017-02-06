import pytest
import requests


@pytest.fixture(params=['www', 'scripts', 'static', 'zeus'])
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


def test_renders_unknown_content(testserver, hostname):
    r = requests.get(
        '%s/text/dummy' % testserver.url,
        headers={'Host': hostname + '.zeit.de'})
    assert r.status_code == 200
    assert r.headers['content-type'] == 'text/plain; charset=UTF-8'
    assert r.headers['Access-Control-Allow-Origin'] == '*'
    assert r.content == 'zeit.web\n'


def test_renders_meta_files(testserver, hostname):
    r = requests.get(
        '%s/text/dummy.meta' % testserver.url,
        headers={'Host': hostname + '.zeit.de'})
    assert r.status_code == 200
    assert r.headers['content-type'] == 'application/xml; charset=UTF-8'
    assert r.headers['Access-Control-Allow-Origin'] == '*'
    assert 'robots.txt' in r.content


@pytest.mark.parametrize('statichost', ['static', 'scripts', 'zeus'])
def test_cannot_access_content_on_static_hosts(testserver, statichost):
    r = requests.get('%s/zeit-online/index' % testserver.url,
                     headers={'Host': statichost + '.zeit.de'},
                     timeout=3600)
    assert r.status_code == 404
    r = requests.get('%s/zeit-online/image/weltall/original' % testserver.url,
                     headers={'Host': statichost + '.zeit.de'})
    assert r.status_code == 404
