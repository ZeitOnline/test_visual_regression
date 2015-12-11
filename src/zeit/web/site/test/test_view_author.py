# -*- coding: utf-8 -*-
import pytest
import zope.component

import zeit.solr.interfaces

import zeit.web.core.interfaces


def test_author_header_should_be_fully_rendered(testbrowser):
    browser = testbrowser('/autoren/j_random')
    header = browser.cssselect('.author-header')
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
    assert len(browser.cssselect('.teaser-small')) == 0


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
    page = browser.cssselect('.pager__page.pager__page--current span')[0].text
    assert page == '2'


def test_author_page_should_hide_favourite_content_on_further_pages(
        testbrowser):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/01'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/02'}]
    browser = testbrowser('/autoren/j_random?p=2')
    assert len(browser.cssselect('.teaser-small')) == 2


@pytest.mark.skipif(
    True, reason='We cannot browser-test this, deduplication happens via solr')
def test_articles_by_author_should_not_repeat_favourite_content(testbrowser):
    pass


def test_first_page_shows_fewer_solr_results_since_it_shows_favourite_content(
        testbrowser):
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    settings['author_articles_page_size'] = 4
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId': 'http://xml.zeit.de/zeit-online/article/01'}]
    browser = testbrowser('/autoren/j_random')
    # 3 favourite_content + 1 solr result
    assert len(browser.cssselect('.teaser-small')) == 4


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


def test_author_biography_should_be_fully_rendered(testbrowser):
    browser = testbrowser('/autoren/j_random')
    container = browser.cssselect('.author-biography')
    summary = container[0].cssselect('.author-summary')
    questions = container[0].cssselect('.author-questions')

    assert len(container) == 1
    assert len(summary) == 1
    assert len(questions) == 1
    assert 'Das ist die Biographie' in summary[0].text
