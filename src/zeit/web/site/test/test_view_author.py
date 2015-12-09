# -*- coding: utf-8 -*-
import zeit.web.site.view_author


def test_author_header_should_be_fully_rendered(testbrowser):
    browser = testbrowser('/autoren/j_random')
    header = browser.cssselect('.author-header')
    name = browser.cssselect('.author-header-info__name')
    summary = browser.cssselect('.author-header-info__summary')
    image = browser.cssselect('.author-header__image')

    assert len(name) == 1
    assert len(summary) == 1
    assert len(image) == 1
    assert 'J. Random Hacker' in name[0].text
    assert 'Random Hacker ist Redakteur' in summary[0].text


def test_author_page_should_show_favourite_content_if_available(testbrowser):
    browser = testbrowser('/autoren/j_random')
    assert len(browser.cssselect('.cp-area--ranking .teaser-small')) == 3


def test_author_page_should_hide_favourite_content_if_missing(testbrowser):
    browser = testbrowser('/autoren/anne_mustermann')
    assert len(browser.cssselect('.cp-area--ranking .teaser-small')) == 0


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
