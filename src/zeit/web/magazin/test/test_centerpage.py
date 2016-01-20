# -*- coding: utf-8 -*-
# import re

# from zope.component import getMultiAdapter
import mock
# import pyramid.threadlocal
# import pytest
import zope.component

# from zeit.cms.checkout.helper import checked_out
# import zeit.cms.interfaces
# import zeit.content.gallery.gallery
# import zeit.cms.syndication.feed

# from zeit.web.core.template import default_image_url
# from zeit.web.core.template import get_teaser_image
# from zeit.web.core.template import get_teaser_template
import zeit.web.core.centerpage
# import zeit.web.magazin.view_centerpage


def test_cp_should_have_buzz_module(
        testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-magazin/test-cp-2015/index' % testserver.url)
    assert '<div class="cp_buzz">' in browser.contents


def test_get_reaches_from_centerpage_view(application):
    settings = zope.component.queryUtility(zeit.web.core.interfaces.ISettings)
    request = mock.Mock()
    request.registry.settings.community_host = settings['community_host']
    request.registry.settings.linkreach_host = settings['linkreach_host']
    request.registry.settings.node_comment_statistics = settings[
        'node_comment_statistics']

    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp-2015/index')
    block = zeit.web.core.utils.find_block(
        cp, module='zmo-buzzbox')
    module = zeit.web.core.template.get_module(block)

    buzz = module.area_buzz

    buzz_views = buzz[0]
    buzz_facebook = buzz[1]
    buzz_comments = buzz[2]

    assert buzz_views[0] == 'views'
    assert buzz_facebook[0] == 'facebook'
    assert buzz_comments[0] == 'comments'

    assert len(buzz_views[1]) == 3
    assert len(buzz_facebook[1]) == 3
    assert len(buzz_comments[1]) == 3
