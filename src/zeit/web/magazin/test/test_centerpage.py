# -*- coding: utf-8 -*-
import zeit.cms.interfaces

import zeit.web.core.utils
import zeit.web.core.template


def test_cp_should_have_buzz_module(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp-2015/buzz')
    assert '<section class="buzzboard">' in browser.contents
    assert '<table class="buzzboard__table' in browser.contents
    assert '<div class="buzzboard__container">' in browser.contents


def test_get_reaches_from_centerpage_view(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp-2015/buzz')
    block = zeit.web.core.utils.find_block(
        cp, module='zmo-mostread')
    buzz = zeit.web.core.template.get_module(block).reach

    buzz_views = buzz.get_views(section='zeit-magazin')[1].score
    buzz_facebook = buzz.get_social(
        facet='facebook', section='zeit-magazin')[1].score
    buzz_comments = buzz.get_comments(section='zeit-magazin')[1].score

    assert buzz_views == 69167
    assert buzz_facebook == 408
    assert buzz_comments == 461
