# -*- coding: utf-8 -*-
from zeit.frontend.test import Browser


def test_footer_exists(testserver):
    browser = Browser('%s/artikel/01' % testserver.url)
    assert '<footer class="main-footer">' in browser.contents


def test_footer_has_logo(testserver):
    browser = Browser('%s/artikel/01' % testserver.url)
    assert '<div class="main-footer__logo'\
        ' icon-zm-logo--white"></div>' in browser.contents
