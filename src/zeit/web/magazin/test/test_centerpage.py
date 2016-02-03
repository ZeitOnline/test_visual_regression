# -*- coding: utf-8 -*-
import re

from zope.component import getMultiAdapter
import mock
import pyramid.threadlocal
import pytest
import zope.component

from zeit.cms.checkout.helper import checked_out
import zeit.cms.interfaces
import zeit.content.gallery.gallery
import zeit.cms.syndication.feed

from zeit.web.core.template import default_image_url
from zeit.web.core.template import get_teaser_image
from zeit.web.core.template import get_teaser_template
import zeit.web.core.centerpage
import zeit.web.magazin.view_centerpage


def test_cp_should_have_buzz_module(
        testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-magazin/test-cp-2015/buzz' % testserver.url)
    assert '<section class="buzzboard">' in browser.contents
    assert '<table class="buzzboard__table' in browser.contents
    assert '<div class="buzzboard__container">' in browser.contents


def test_get_reaches_from_centerpage_view(application):
    settings = zope.component.queryUtility(zeit.web.core.interfaces.ISettings)
    request = mock.Mock()
    request.registry.settings.community_host = settings['community_host']
    request.registry.settings.linkreach_host = settings['linkreach_host']
    request.registry.settings.node_comment_statistics = settings[
        'node_comment_statistics']

    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp-2015/buzz')
    block = zeit.web.core.utils.find_block(
        cp, module='zmo-mostread')
    module = zeit.web.core.template.get_module(block)
    buzz = module.reach

    buzz_views = buzz.get_views(section='zeit-magazin')[1].score
    buzz_facebook = buzz.get_social(
        facet='facebook', section='zeit-magazin')[1].score
    buzz_comments = buzz.get_comments(section='zeit-magazin')[1].score

    assert buzz_views == 69167
    assert buzz_facebook == 408
    assert buzz_comments == 461


def test_teaser_square_large_has_expected_structure(testbrowser):
    browser = testbrowser('/centerpage/lebensart')
    wrap = browser.cssselect('.teaser-square-large')
    assert len(wrap) != 0
    for element in wrap:
        text_wrap = element.cssselect('.teaser-square-large__text')
        link_wrap = element.cssselect('a')
        image_wrap = element.cssselect('.teaser-square-large__asset')
        assert len(text_wrap) != 0
        assert len(link_wrap) == 1
        assert len(image_wrap) != 0
