# -*- coding: utf-8 -*-
import json


def test_amp_view_should_have_expected_structure(testbrowser):
    browser = testbrowser('/amp/zeit-magazin/article/01')
    link = browser.cssselect('head link[rel="canonical"]')[0]
    article = browser.cssselect('article.article')[0]
    image = article.cssselect('figure.figure')[0]

    assert ('<html ⚡ lang="de">') in browser.contents
    assert link.get('href') == 'http://localhost/zeit-magazin/article/01'
    assert 'figure--large' in image.get('class')


def test_amp_view_should_consider_image_display_mode(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/image-column-width')
    article = browser.cssselect('article.article')[0]
    image = article.cssselect('figure.figure')[1]

    assert 'figure--column-width' in image.get('class')


def test_amp_view_should_ignore_header_image_display_mode(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/image-column-width')
    article = browser.cssselect('article.article')[0]
    image = article.cssselect('figure.figure')[0]

    assert 'figure--large' in image.get('class')


def test_amp_contains_required_structured_data(testbrowser):
    browser = testbrowser('/amp/zeit-magazin/article/01')
    scripts = browser.cssselect('head script[type="application/ld+json"]')
    data = {}

    assert scripts

    for script in scripts:
        content = json.loads(script.text_content().strip())
        data[content['@type']] = content

    page = data['WebPage']
    article = data['Article']
    publisher = data['Organization']
    breadcrumb = data['BreadcrumbList']

    # check WebPage
    assert page['publisher']['@id'] == publisher['@id']
    assert page['mainEntity']['@id'] == article['@id']
    assert page['breadcrumb']['@id'] == breadcrumb['@id']

    # check Organization
    assert publisher['@id'] == '#publisher'
    assert publisher['name'] == 'ZEITmagazin'
    assert publisher['url'] == 'http://localhost/zeit-magazin/index'
    assert publisher['logo']['@type'] == 'ImageObject'
    assert publisher['logo']['url'] == (
        'http://localhost/static/latest/images/'
        'structured-data-publisher-logo-zmo.png')
    assert publisher['logo']['width'] == 600
    assert publisher['logo']['height'] == 56

    # check Article
    assert article['mainEntityOfPage']['@id'] == (
        'http://localhost/zeit-magazin/article/01')
    assert article['headline'] == u'Gentrifizierung: Mei, is des traurig!'
    assert len(article['description'])
    assert article['datePublished'] == '2013-09-26T08:00:00+02:00'
    assert article['dateModified'] == '2013-10-08T11:25:03+02:00'
    assert article['keywords'] == (
        u'Gentrifizierung, Christian Ude, Facebook, Mietvertrag, München')
    assert article['publisher']['@id'] == publisher['@id']

    # check ImageObject
    assert article['image']['@type'] == 'ImageObject'
    assert article['image']['url'] == (
        'http://localhost/exampleimages/artikel/01/schoppenstube/'
        'wide__1300x731')
    assert article['image']['width'] == 1300
    assert article['image']['height'] == 731

    # check author
    assert article['author']['@type'] == 'Person'
    assert article['author']['name'] == 'Anne Mustermann'
    assert article['author']['url'] == (
        'http://localhost/autoren/anne_mustermann')


def test_amp_article_shows_zplus_badge_for_paid_article(testbrowser):
    browser = testbrowser('/amp/zeit-magazin/article/zplus-zmo-paid')
    badge = browser.cssselect('.zplus-badge')[0]
    text = badge.cssselect('.zplus-badge__text')[0]

    assert text.text.strip() == u'Exklusiv für Abonnenten'
    assert badge.cssselect('.zplus-badge__icon')


def test_amp_article_shows_no_zplus_badge_for_metered_article(
        testbrowser):
    browser = testbrowser('/amp/zeit-magazin/article/zplus-zmo-register')
    assert not browser.cssselect('.zplus-badge')


def test_amp_article_shows_no_zplus_badge_for_free_article(testbrowser):
    browser = testbrowser('/amp/zeit-magazin/article/03')
    assert not browser.cssselect('.zplus-badge')
