import requests


def test_amp_disabled_articles_should_redirect_accordingly(testserver):
    resp = requests.get(testserver.url + '/amp/zeit-online/article/01?foo=42',
                        allow_redirects=False)
    assert resp.headers.get('Location') == (
        testserver.url + '/zeit-online/article/01?foo=42')
    assert resp.status_code == 302
