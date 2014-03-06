from zope.testbrowser.browser import Browser
import mock
import pytest
import requests

def test_centerpage_should_have_expected_markup(testserver):
    browser = Browser('%s/centerpage/lebensart' % testserver.url)
    assert 'FOO' in browser.contents
