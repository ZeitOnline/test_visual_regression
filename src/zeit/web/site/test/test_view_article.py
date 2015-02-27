# -*- coding: utf-8 -*-

import zeit.cms.interfaces


def test_article_should_render_full_view(testserver, testbrowser):
    article_path = '{}/zeit-online/article/zeit{}'
    browser = testbrowser(article_path.format(
        testserver.url, '/komplettansicht'))
    article = zeit.cms.interfaces.ICMSContent(
        article_path.format('http://xml.zeit.de', ''))
    assert len(browser.cssselect('p.paragraph')) == article.paragraphs
