# -*- coding: utf-8 -*-


def test_footer_exists(testserver, testbrowser):
    browser = testbrowser('%s/artikel/01' % testserver.url)
    assert '<footer class="main-footer">' in browser.contents


def test_footer_has_logo(testserver, testbrowser):
    browser = testbrowser('%s/artikel/01' % testserver.url)
    assert '<div class="main-footer__logo'\
        ' icon-logo-zmo-small"></div>' in browser.contents
