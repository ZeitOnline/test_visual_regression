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


def test_amp_liveblog_v2_article_contains_required_styles(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/liveblog')
    assert '#livedesk-root' in browser.contents
    assert '.lb-timeline' not in browser.contents


def test_amp_liveblog_v3_article_contains_required_styles(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/liveblog3')
    assert '#livedesk-root' not in browser.contents
    assert '.lb-timeline' in browser.contents


def test_amp_liveblog_v3_article_contains_required_markup(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/liveblog3')
    article = browser.cssselect('article.article')[0]
    head = browser.cssselect('head')[0]
    # liveblog status for liveblog article template
    assert browser.cssselect('.liveblog-status')
    assert article.get('itemtype') == 'http://schema.org/LiveBlogPosting'
    # required script for AMP live list
    assert head.cssselect('script[custom-element="amp-facebook"]')
    assert head.cssselect('script[custom-element="amp-iframe"]')
    assert head.cssselect('script[custom-element="amp-image-lightbox"]')
    assert head.cssselect('script[custom-element="amp-instagram"]')
    assert head.cssselect('script[custom-element="amp-live-list"]')
    assert head.cssselect('script[custom-element="amp-social-share"]')
    assert head.cssselect('script[custom-element="amp-soundcloud"]')
    assert head.cssselect('script[custom-element="amp-timeago"]')
    assert head.cssselect('script[custom-element="amp-twitter"]')
    assert head.cssselect('script[custom-element="amp-youtube"]')
    # main image before article header
    assert article.cssselect('[itemprop="mainEntity"] [itemprop="image"]')
    assert not article.cssselect('[itemprop="articleBody"] [itemprop="image"]')
