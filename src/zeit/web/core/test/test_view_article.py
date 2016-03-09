import mock
import requests

import zeit.cms.interfaces
import zeit.web.core.view_article


def test_amp_disabled_articles_should_redirect_accordingly(testserver):
    resp = requests.get(testserver.url + '/amp/zeit-online/article/01?foo=42',
                        allow_redirects=False)
    assert resp.headers.get('Location') == (
        testserver.url + '/zeit-online/article/01?foo=42')
    assert resp.status_code == 302


def test_article_tags_template_renders_rel_attribute(
        tplbrowser, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/tags')
    view = zeit.web.core.view_article.Article(context, dummy_request)
    # there is an unsolved issue with dummy_request here
    # route_url raises ComponentLookupError
    request = mock.Mock()
    request.route_url = lambda x: "http://example.com/"
    browser = tplbrowser(
        'zeit.web.core:templates/inc/article/tags.html',
        view=view,
        request=request)
    tags = browser.cssselect('a.article-tags__link')
    for tag in tags:
        assert tag.get('rel') == 'tag'
