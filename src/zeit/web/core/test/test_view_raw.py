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
    assert r.content == 'zeit.web\n'


def test_renders_unknown_content(testserver, hostname):
    r = requests.get(
        '%s/text/dummy' % testserver.url,
        headers={'Host': hostname + '.zeit.de'})
    assert r.status_code == 200
    assert r.headers['content-type'] == 'text/plain; charset=UTF-8'
    assert r.content == 'zeit.web\n'


def test_renders_meta_files(testserver, hostname):
    r = requests.get(
        '%s/text/dummy.meta' % testserver.url,
        headers={'Host': hostname + '.zeit.de'})
    assert r.status_code == 200
    assert r.headers['content-type'] == 'application/xml; charset=UTF-8'
    assert 'robots.txt' in r.content
