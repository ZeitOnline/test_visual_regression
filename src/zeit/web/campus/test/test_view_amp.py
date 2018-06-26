# -*- coding: utf-8 -*-
import json


def test_amp_view_should_have_expected_structure(testbrowser):
    browser = testbrowser('/amp/campus/article/common')
    link = browser.cssselect('head link[rel="canonical"]')[0]
    article = browser.cssselect('article.article')[0]
    image = article.cssselect('figure.figure')[0]

    assert ('<html ⚡ lang="de">') in browser.contents
    assert link.get('href') == 'http://localhost/campus/article/common'
    assert 'figure--large' in image.get('class')


def test_amp_contains_required_structured_data(testbrowser):
    browser = testbrowser('/amp/campus/article/common')
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
    assert publisher['name'] == 'ZEIT Campus'
    assert publisher['url'] == 'http://localhost/campus/index'
    assert publisher['logo']['@type'] == 'ImageObject'
    assert publisher['logo']['url'] == (
        'http://localhost/static/latest/images/'
        'structured-data-publisher-logo-zco.png')
    assert publisher['logo']['width'] == 347
    assert publisher['logo']['height'] == 60

    # check Article
    assert article['mainEntityOfPage']['@id'] == (
        'http://localhost/campus/article/common')
    assert article['headline'] == u'"Der Hobbit": Geht\'s noch größer?'
    assert len(article['description'])
    assert article['datePublished'] == '2016-02-09T08:36:17+01:00'
    assert article['dateModified'] == '2016-02-10T10:39:16+01:00'
    assert article['keywords'] == (
        u'Student, Hochschule, Auslandssemester, Bafög-Antrag, Praktikum, '
        u'Studienfinanzierung')
    assert article['publisher']['@id'] == publisher['@id']

    # check ImageObject
    assert article['image']['@type'] == 'ImageObject'
    assert article['image']['url'] == (
        'http://localhost/campus/image/jura-studium-fleiss/wide__1300x731')
    assert article['image']['width'] == 1300
    assert article['image']['height'] == 731

    # check author
    assert article['author']['@type'] == 'Person'
    assert article['author']['name'] == 'Wenke Husmann'
    assert article['author']['url'] == (
        'http://localhost/autoren/H/Wenke_Husmann/index.xml')
