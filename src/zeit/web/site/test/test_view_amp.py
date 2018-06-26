# -*- coding: utf-8 -*-
import datetime
import json
import pytest


def test_amp_article_contains_no_unwanted_liveblog_addition(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/amp')
    article = browser.cssselect('article.article')[0]
    # no liveblog status for default article template
    assert not browser.cssselect('.liveblog-status')
    # no additional script for AMP live list
    assert not browser.cssselect('script[custom-element="amp-live-list"]')
    # main image after headline
    assert article.cssselect('h1.headline ~ div amp-img')


def test_amp_standard_article_contains_required_liveblog_addition(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/liveblog')
    article = browser.cssselect('article.article')[0]
    # no liveblog status for default article template
    assert not browser.cssselect('.liveblog-status')
    # required script for AMP live list
    assert browser.cssselect('script[custom-element="amp-live-list"]')
    # main image after headline with layout large
    assert article.cssselect('h1.headline ~ div .figure--large amp-img')


def test_amp_liveblog_article_contains_required_liveblog_addition(testbrowser):
    browser = testbrowser('/amp/zeit-online/liveblog/champions-league')
    article = browser.cssselect('article.article')[0]
    header = article.cssselect('header')[0]
    # liveblog status for liveblog article template
    assert browser.cssselect('.liveblog-status')
    # required script for AMP live list
    assert browser.cssselect('script[custom-element="amp-live-list"]')
    # main image before headline with layout column-width
    assert header[0].cssselect('.figure--column-width amp-img')
    assert not header.cssselect('.figure--large')
    assert header[1].cssselect('h1.headline')


def test_amp_liveblog_article_contains_required_structured_data(testbrowser):
    browser = testbrowser('/amp/zeit-online/liveblog/champions-league')
    scripts = browser.cssselect('head script[type="application/ld+json"]')
    data = {}

    assert scripts

    for script in scripts:
        content = json.loads(script.text_content().strip())
        data[content['@type']] = content

    page = data['WebPage']
    liveblog = data['LiveBlogPosting']
    publisher = data['Organization']
    breadcrumb = data['BreadcrumbList']

    # check WebPage
    assert page['publisher']['@id'] == publisher['@id']
    assert page['mainEntity']['@id'] == liveblog['@id']
    assert page['breadcrumb']['@id'] == breadcrumb['@id']

    # check Liveblog
    assert liveblog['mainEntityOfPage']['@id'] == (
        'http://localhost/zeit-online/liveblog/champions-league')
    assert liveblog['headline'] == (
        u'Live-Blog Champions League: Und dann kam Messi')
    assert len(liveblog['description'])
    assert liveblog['datePublished'] == '2015-05-06T20:11:02+02:00'
    assert liveblog['dateModified'] == '2015-05-06T23:52:15+02:00'
    assert liveblog['coverageStartTime'] == '2015-05-06T20:11:02+02:00'
    assert liveblog['coverageEndTime'] == '2015-05-06T23:52:15+02:00'
    assert liveblog['keywords'] == (
        u'Pep Guardiola, Champions League, FC Bayern München, FC Barcelona')
    assert liveblog['publisher']['@id'] == publisher['@id']


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
    header = article.cssselect('header')[0]
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
    # main image before headline with layout column-width
    assert header[0].cssselect('.figure--column-width amp-img')
    assert not header.cssselect('.figure--large')
    assert header[1].cssselect('h1.headline')


def test_amp_liveblog_v3_article_contains_required_structured_data(
        testbrowser):
    browser = testbrowser('/amp/zeit-online/article/liveblog3')
    scripts = browser.cssselect('head script[type="application/ld+json"]')
    data = {}

    assert scripts

    for script in scripts:
        content = json.loads(script.text_content().strip())
        data[content['@type']] = content

    page = data['WebPage']
    liveblog = data['LiveBlogPosting']
    publisher = data['Organization']
    breadcrumb = data['BreadcrumbList']

    # check WebPage
    assert page['publisher']['@id'] == publisher['@id']
    assert page['mainEntity']['@id'] == liveblog['@id']
    assert page['breadcrumb']['@id'] == breadcrumb['@id']

    # check Liveblog
    assert liveblog['mainEntityOfPage']['@id'] == (
        'http://localhost/zeit-online/article/liveblog3')
    assert liveblog['headline'] == u'Liveblog 3: Testblog'
    assert len(liveblog['description'])
    assert liveblog['datePublished'] == '2018-02-09T13:00:00+01:00'
    assert liveblog['dateModified'] == '2018-02-09T13:00:00+01:00'
    assert liveblog['coverageStartTime'] == '2018-02-09T13:00:00+01:00'
    assert liveblog['coverageEndTime'] == '2018-02-09T13:00:00+01:00'
    assert 'keywords' not in liveblog
    assert liveblog['publisher']['@id'] == publisher['@id']


def test_amp_liveblog_v3_solo_article_contains_required_markup(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/liveblog3-solo-theme')
    article = browser.cssselect('article.article')[0]
    header = article.cssselect('header')[0]
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
    # main image before headline with layout column-width
    assert header[0].cssselect('.figure--column-width amp-img')
    assert not header.cssselect('.figure--large')
    assert header[1].cssselect('h1.headline')


def test_amp_liveblog_v3_solo_article_contains_required_structured_data(
        testbrowser):
    browser = testbrowser('/amp/zeit-online/article/liveblog3-solo-theme')
    scripts = browser.cssselect('head script[type="application/ld+json"]')
    data = {}

    assert scripts

    for script in scripts:
        content = json.loads(script.text_content().strip())
        data[content['@type']] = content

    page = data['WebPage']
    liveblog = data['LiveBlogPosting']
    publisher = data['Organization']
    breadcrumb = data['BreadcrumbList']

    # check WebPage
    assert page['publisher']['@id'] == publisher['@id']
    assert page['mainEntity']['@id'] == liveblog['@id']
    assert page['breadcrumb']['@id'] == breadcrumb['@id']

    # check Liveblog
    assert liveblog['mainEntityOfPage']['@id'] == (
        'http://localhost/zeit-online/article/liveblog3-solo-theme')
    assert liveblog['headline'] == u'Liveblog 3: ZON Default Solo Theme'
    assert len(liveblog['description'])
    assert liveblog['datePublished'] == '2018-02-09T13:00:00+01:00'
    assert liveblog['dateModified'] == '2018-02-09T13:00:00+01:00'
    assert liveblog['coverageStartTime'] == '2018-02-09T13:00:00+01:00'
    assert liveblog['coverageEndTime'] == '2018-02-09T13:00:00+01:00'
    assert 'keywords' not in liveblog
    assert liveblog['publisher']['@id'] == publisher['@id']


def test_amp_liveblog_v3_article_last_modified_date(testbrowser, clock):
    clock.freeze(datetime.datetime(2018, 2, 9, 12, 28))
    browser = testbrowser('/amp/zeit-online/article/liveblog3')

    # liveblog status for liveblog article template
    assert browser.cssselect('.liveblog-status')
    assert browser.cssselect('.liveblog-status__meta-date')[0].text == (
        '9. Februar 2018')
    assert browser.cssselect('.liveblog-status__meta-updated')[0].text == (
        'vor 28 Minuten aktualisiert')


@pytest.mark.parametrize('article, length, name, url', [
    ('amp', 1, 'Jochen Wegner', 'autoren/W/Jochen_Wegner/index'),
    ('liveblog', 2, 'Oliver Fritsch', 'autoren/F/Oliver_Fritsch-2/index'),
    ('amp-ohne-autor', 1, 'ZEITmagazin', None),
    ('dpa', 1, 'DPA', None)])
def test_amp_article_contains_structured_data_for_author(
        article, length, name, url, testbrowser):
    browser = testbrowser('/amp/zeit-online/article/{}'.format(article))
    scripts = browser.cssselect('head script[type="application/ld+json"]')
    data = {}

    assert scripts

    for script in scripts:
        content = json.loads(script.text_content().strip())
        data[content['@type']] = content

    article = data['Article']

    if length > 1:
        assert len(article['author']) == length
        author = article['author'][1]
    else:
        author = article['author']

    # check article author
    assert author['@type'] == 'Person'
    assert author['name'] == name
    if url:
        assert author['url'] == 'http://localhost/{}'.format(url)
    else:
        assert 'url' not in author
