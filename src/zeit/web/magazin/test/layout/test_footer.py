# -*- coding: utf-8 -*-


def test_footer_exists(testbrowser):
    browser = testbrowser('/artikel/01')
    assert '<footer class="main-footer">' in browser.contents


def test_footer_has_logo(testbrowser):
    browser = testbrowser('/artikel/01')
    assert '<svg class="svg-symbol main-footer__logo' in browser.contents
