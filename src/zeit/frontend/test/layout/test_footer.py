import pytest
from zope.testbrowser.browser import Browser


def test_footer_exists(testserver):
    browser = Browser('%s/artikel/01' % testserver.url)
    assert '<footer class="main-footer">' in browser.contents


def test_footer_has_logo(testserver):
    browser = Browser('%s/artikel/01' % testserver.url)
    assert '<span class="main-footer__ZM__img'\
        ' icon-zm-logo--white"></span>' in browser.contents
