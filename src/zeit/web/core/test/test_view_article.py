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
    browser = tplbrowser(
        'zeit.web.core:templates/inc/article/tags.html',
        view=view, request=dummy_request)
    tags = browser.cssselect('a.article-tags__link')
    for tag in tags:
        assert tag.get('rel') == 'tag'


def test_instantarticle_shows_ad_after_100_words(testbrowser):
    word_count = 0
    bro = testbrowser('/instantarticle/zeit-online/article/simple-multipage')
    blocks = bro.xpath('body/article/*')
    blocks = blocks[1:]
    for block in blocks:
        if block.tag == 'p':
            words = len(block.text_content().strip().split())
            word_count = word_count + words
        if block.tag == 'figure':
            break
    assert word_count > 100
