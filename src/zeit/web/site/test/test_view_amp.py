# -*- coding: utf-8 -*-


def test_amp_article_contains_no_unwanted_liveblog_addition(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/amp')
    article = browser.cssselect('article.article')[0]
    # no liveblog status for default article template
    assert not browser.cssselect('.liveblog-status')
    assert article.get('itemtype') == 'http://schema.org/Article'
    # no additional script for AMP live list
    assert not browser.cssselect('script[custom-element="amp-live-list"]')
    # main image inside article body
    assert article.cssselect('[itemprop="articleBody"] [itemprop="image"]')


def test_amp_standard_article_contains_required_liveblog_addition(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/liveblog')
    article = browser.cssselect('article.article')[0]
    # no liveblog status for default article template
    assert not browser.cssselect('.liveblog-status')
    assert article.get('itemtype') == 'http://schema.org/LiveBlogPosting'
    # required script for AMP live list
    assert browser.cssselect('script[custom-element="amp-live-list"]')
    # main image inside article body
    assert article.cssselect('[itemprop="articleBody"] [itemprop="image"]')


def test_amp_liveblog_article_contains_required_liveblog_addition(testbrowser):
    browser = testbrowser('/amp/zeit-online/liveblog/champions-league')
    article = browser.cssselect('article.article')[0]
    # liveblog status for liveblog article template
    assert browser.cssselect('.liveblog-status')
    assert article.get('itemtype') == 'http://schema.org/LiveBlogPosting'
    # required script for AMP live list
    assert browser.cssselect('script[custom-element="amp-live-list"]')
    # main image before article header
    assert article.cssselect('[itemprop="mainEntity"] [itemprop="image"]')
    assert not article.cssselect('[itemprop="articleBody"] [itemprop="image"]')
