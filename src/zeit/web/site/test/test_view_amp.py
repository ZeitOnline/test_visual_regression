# -*- coding: utf-8 -*-
import datetime


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
    # main image inside article header with layout large
    assert article.cssselect('header [itemprop="image"].figure--large')


def test_amp_liveblog_article_contains_required_liveblog_addition(testbrowser):
    browser = testbrowser('/amp/zeit-online/liveblog/champions-league')
    article = browser.cssselect('article.article')[0]
    # liveblog status for liveblog article template
    assert browser.cssselect('.liveblog-status')
    assert article.get('itemtype') == 'http://schema.org/LiveBlogPosting'
    # required script for AMP live list
    assert browser.cssselect('script[custom-element="amp-live-list"]')
    # main image inside article header with layout column-width
    assert article.cssselect('header [itemprop="image"].figure--column-width')
    assert not article.cssselect('header [itemprop="image"].figure--large')


def test_amp_liveblog_v2_article_contains_required_styles(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/liveblog')
    styles = browser.cssselect('style[amp-custom]')
    assert len(styles) == 1
    assert '#livedesk-root' in styles[0].text
    assert '.lb-timeline' not in styles[0].text


def test_amp_liveblog_v3_article_contains_required_styles(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/liveblog3')
    styles = browser.cssselect('style[amp-custom]')
    assert len(styles) == 1
    assert '#livedesk-root' not in styles[0].text
    assert '.lb-timeline' in styles[0].text


def test_amp_liveblog_v3_article_contains_required_markup(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/liveblog3')
    article = browser.cssselect('article.article')[0]
    head = browser.cssselect('head')[0]
    # required script for AMP live list
    assert head.cssselect('script[custom-element="amp-facebook"]')
    assert head.cssselect('script[custom-element="amp-iframe"]')
    assert head.cssselect('script[custom-element="amp-image-lightbox"]')
    assert head.cssselect('script[custom-element="amp-instagram"]')
    assert head.cssselect('script[custom-element="amp-live-list"]')
    assert head.cssselect('script[custom-element="amp-social-share"]')
    assert head.cssselect('script[custom-element="amp-soundcloud"]')
    assert head.cssselect('script[custom-element="amp-twitter"]')
    assert head.cssselect('script[custom-element="amp-youtube"]')
    assert not head.cssselect('script[custom-element="amp-timeago"]')
    # structured data for LiveBlogPosting
    assert article.get('itemtype') == 'http://schema.org/LiveBlogPosting'
    # main image before article header
    assert article.cssselect('[itemprop="mainEntity"] [itemprop="image"]')
    assert not article.cssselect('[itemprop="articleBody"] [itemprop="image"]')
    # structured data for coverage time
    assert article.cssselect('[itemprop="coverageStartTime"]')[0].get(
        'content') == '2018-02-09T13:00:00+01:00'
    assert article.cssselect('[itemprop="coverageEndTime"]')[0].get(
        'content') == '2018-02-02T14:31:50+01:00'


def test_amp_liveblog_v3_solo_article_contains_required_markup(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/liveblog3-solo-theme')
    article = browser.cssselect('article.article')[0]
    head = browser.cssselect('head')[0]
    # required script for AMP live list
    assert head.cssselect('script[custom-element="amp-facebook"]')
    assert head.cssselect('script[custom-element="amp-iframe"]')
    assert head.cssselect('script[custom-element="amp-image-lightbox"]')
    assert head.cssselect('script[custom-element="amp-instagram"]')
    assert head.cssselect('script[custom-element="amp-live-list"]')
    assert head.cssselect('script[custom-element="amp-social-share"]')
    assert head.cssselect('script[custom-element="amp-soundcloud"]')
    assert head.cssselect('script[custom-element="amp-twitter"]')
    assert head.cssselect('script[custom-element="amp-youtube"]')
    assert head.cssselect('script[custom-element="amp-timeago"]')
    # structured data for LiveBlogPosting
    assert article.get('itemtype') == 'http://schema.org/LiveBlogPosting'
    # main image before article header
    assert article.cssselect('[itemprop="mainEntity"] [itemprop="image"]')
    assert not article.cssselect('[itemprop="articleBody"] [itemprop="image"]')
    # structured data for coverage time
    assert article.cssselect('[itemprop="coverageStartTime"]')[0].get(
        'content') == '2018-02-09T13:00:00+01:00'
    assert article.cssselect('[itemprop="coverageEndTime"]')[0].get(
        'content') == '2017-12-05T16:12:54+01:00'


def test_amp_liveblog_v3_article_last_modified_date(testbrowser, clock):
    clock.freeze(datetime.datetime(2018, 2, 2, 14, 0))
    browser = testbrowser('/amp/zeit-online/article/liveblog3')

    # liveblog status for liveblog article template
    assert browser.cssselect('.liveblog-status')
    assert browser.cssselect('.liveblog-status__meta-date')[0].text == (
        '2. Februar 2018')
    assert browser.cssselect('.liveblog-status__meta-updated')[0].text == (
        'vor 28 Minuten aktualisiert')
