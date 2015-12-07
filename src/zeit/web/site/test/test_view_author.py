# -*- coding: utf-8 -*-
import zeit.web.site.view_author


def test_author_header_should_be_fully_rendered(testserver, testbrowser):
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
