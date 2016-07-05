# -*- coding: utf-8 -*-
import datetime
import lxml.html
import pyramid.testing
import pytest
import zope.component

import zeit.solr.interfaces

import zeit.web.core.interfaces


def test_author_page_contains_main_navigation(testbrowser):
    browser = testbrowser('/autoren/j_random')
    header = browser.cssselect('header.header')[0]
    assert header.cssselect('.nav')
    assert header.cssselect('.nav__ressorts')


def test_author_header_should_be_fully_rendered(testbrowser):
    browser = testbrowser('/autoren/j_random')
    name = browser.cssselect('.author-header__name')
    summary = browser.cssselect('.author-header__summary')
    image = browser.cssselect('.author-header__image')

    assert len(name) == 1
    assert len(summary) == 1
    assert len(image) == 1
    assert 'J. Random Hacker' in name[0].text
    assert 'Random Hacker ist Redakteur' in summary[0].text


def test_author_page_should_show_favourite_content_if_available(testbrowser):
    browser = testbrowser('/autoren/j_random')
    assert len(browser.cssselect('.teaser-small')) == 3


def test_author_page_should_hide_favourite_content_if_missing(testbrowser):
    browser = testbrowser('/autoren/anne_mustermann')
    assert len(browser.cssselect('.cp-area--ranking .teaser-small')) == 0
    assert len(browser.cssselect('.teaser-small')) == 0


def test_author_page_should_feature_schema_org_props(testbrowser):
    doc = testbrowser('/autoren/anne_mustermann').document
    name = doc.xpath('//*[@itemprop="author"]/*[@itemprop="name"]')
    assert name[0].text.strip() == 'Anne Mustermann'


def test_author_page_should_show_articles_by_author(testbrowser):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/01'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/02'}]
    browser = testbrowser('/autoren/anne_mustermann')
    assert len(browser.cssselect('.teaser-small')) == 2


def test_articles_by_author_should_paginate(testbrowser):
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    settings['author_articles_page_size'] = 1
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/01'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/02'}]
    browser = testbrowser('/autoren/anne_mustermann?p=2')
    assert len(browser.cssselect('.teaser-small')) == 1
    page = browser.cssselect('.pager__page--current')[0]
    assert page.text_content().strip() == '2'


def test_author_page_should_hide_favourite_content_on_further_pages(
        testbrowser):
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    settings['author_articles_page_size'] = 4
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
        {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/01'},
        {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/02'},
        {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/03'},
        {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/04'},
        {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/05'},
        {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/06'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/01'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/02'}]
    # we have 8 solr hits + 3 favorite articles
    # we expect 3 pages, considering page_size = 4
    # page 1: 3 favorites + 1 more, adds up to 4
    # page 2: 4 articles - should be result no. 2-5
    # page 3: the remaining 3 articles - result no. 6-8
    select = testbrowser('/autoren/j_random').cssselect
    assert len(select('.cp-area--author-favourite-content')) == 1
    assert len(select('.cp-area--author-favourite-content article')) == 3
    assert len(select('.cp-area--author-articles article')) == 1
    assert len(select('.teaser-small')) == 4
    assert len(select('.pager__pages .pager__page')) == 3
    select = testbrowser('/autoren/j_random?p=2').cssselect
    assert len(select('.cp-area--author-favourite-content')) == 0
    assert len(select('.teaser-small')) == 4
    select = testbrowser('/autoren/j_random?p=3').cssselect
    assert len(select('.teaser-small')) == 3


@pytest.mark.skipif(
    True, reason='We cannot browser-test this, deduplication happens via solr')
def test_articles_by_author_should_not_repeat_favourite_content(testbrowser):
    pass


def test_first_page_shows_fewer_solr_results_since_it_shows_favourite_content(
        testbrowser):
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    settings['author_articles_page_size'] = 4
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/01'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/02'}]
    browser = testbrowser('/autoren/j_random')
    # 3 favourite_content + 1 solr result
    assert len(browser.cssselect('.teaser-small')) == 4


def test_view_author_comments_should_have_comments_area(
        application, dummy_request):
    author = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/autoren/author3')
    request = dummy_request
    request.registry.settings = {'author_comment_page_size': '6'}
    request.GET = {'p': '1'}
    view = zeit.web.site.view_author.Comments(author, request)
    assert type(view.tab_areas[0]) == (
        zeit.web.site.view_author.UserCommentsArea)


def test_author_contact_should_be_fully_rendered(testbrowser):
    browser = testbrowser('/autoren/j_random')
    container = browser.cssselect('.author-contact')[0]
    items = container.cssselect('.author-contact__item')
    twitter = container.cssselect('.author-contact__icon--twitter')
    facebook = container.cssselect('.author-contact__icon--facebook')
    instagram = container.cssselect('.author-contact__icon--instagram')

    assert len(items) == 3
    assert len(twitter) == 1
    assert len(facebook) == 1
    assert len(instagram) == 1


def test_author_should_have_user_comments(testbrowser, clock):
    clock.freeze(datetime.datetime(2015, 12, 9))
    browser = testbrowser('/autoren/author3/kommentare')

    comments = browser.cssselect('.user-comment')

    # comment *without* title
    assert 'Ich habe den Halbsatz' in comments[0].cssselect(
        '.user-comment__text > p')[0].text
    # comment *with* title
    assert 'Hmmmmmm' == comments[1].cssselect(
        '.user-comment__text > p')[0].text

    assert '17. November 2015, verfasst zu:' == comments[0].cssselect(
        '.user-comment__date')[0].text

    assert '?cid=5572182#cid-5572182' in comments[0].cssselect(
        '.user-comment__article-link')[0].attrib['href']


def test_author_biography_should_be_fully_rendered(testbrowser):
    browser = testbrowser('/autoren/j_random')
    bio = browser.cssselect('.author-biography')
    assert 'Das ist die Biographie' in bio[0].text
    summary = browser.cssselect('.author-header__summary')
    assert 'Redakteur im Ressort Digital' in summary[0].text
    assert browser.cssselect('.author-questions')


def test_author_first_favorite_article_forces_mobile_image(application):
    author = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/autoren/j_random')
    request = pyramid.testing.DummyRequest()
    view = zeit.web.site.view_author.Author(author, request)
    teasers = view.area_favourite_content.values()
    assert teasers[0].force_mobile_image
    assert not teasers[1].force_mobile_image


def test_author_handles_missing_profile_data_right(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/author/profile.html')
    author = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/autoren/j_random')
    author.topiclink_url_1 = None
    author.topiclink_url_2 = None
    author.topiclink_url_3 = None
    author.biography = ''
    author.twitter = ''
    author.facebook = ''
    author.instagram = ''
    author.bio_questions['hobby'] = None
    author.bio_questions['person'] = None
    request = pyramid.testing.DummyRequest()
    view = zeit.web.site.view_author.Author(author, request)
    html_str = tpl.render(view=view, context=view.context)
    select = lxml.html.fromstring(html_str).cssselect

    assert len(select('.author-topics')) == 0
    assert len(select('.author-biography')) == 0
    assert len(select('.author-contact')) == 0
    assert len(select('.author-questions__text')) == 5


def test_author_has_correct_open_graph_image(testbrowser):
    select = testbrowser('/autoren/julia_zange').cssselect
    url = ('http://localhost/zeit-online/cp-content/'
           'author_images/Julia_Zange/wide__1300x731')
    assert select('meta[property="og:image"]')[0].get('content') == url
    assert select('meta[property="og:image:width"]')[0].get('content') == (
        '1300')
    assert select('meta[property="og:image:height"]')[0].get('content') == (
        '731')
    assert select('meta[name="twitter:image"]')[0].get('content') == url
    assert select('link[rel="image_src"]')[0].get('href') == url
