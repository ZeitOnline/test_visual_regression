# -*- coding: utf-8 -*-
from zeit.web.core.test import Browser


def test_footer_exists(testserver):
    browser = Browser('%s/artikel/01' % testserver.url)
    assert '<footer class="main-footer">' in browser.contents


def test_footer_has_logo(testserver):
    browser = Browser('%s/artikel/01' % testserver.url)
    assert '<div class="main-footer__logo'\
        ' icon-logo-zmo-small"></div>' in browser.contents
