# -*- coding: utf-8 -*-
import mock
import pytest

import zeit.cms.interfaces

import zeit.web.core.banner
import zeit.web.site

def is_adcontrolled(contents):
    return 'data-adDeliveryType="adcontroller"' in contents


def test_banner_toggles_should_return_value(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/zeitonline')
    view = zeit.web.site.view_centerpage.Centerpage(context, mock.Mock())
    assert view.banner_toggles('testing_me') is False


def test_adcontroller_head_code_is_present(testserver, testbrowser):
    browser = testbrowser('%s/zeit-online/index' % testserver.url)
    if not is_adcontrolled(browser.contents):
        pytest.skip("not applicable due to oldschool ad configuration")

    assert '<!-- ad controller head start -->' in browser.contents
    assert '<!-- adcontroller load -->' in browser.contents
    assert '<!-- mandanten object -->' in browser.contents


def test_adcontroller_adtags_are_present(testserver, testbrowser):
    browser = testbrowser('%s/zeit-online/index' % testserver.url)
    if not is_adcontrolled(browser.contents):
        pytest.skip("not applicable due to oldschool ad configuration")

    assert 'AdController.render(\'iqadtile1\');' in browser.contents
    assert 'AdController.render(\'iqadtile2\');' in browser.contents
    assert 'AdController.render(\'iqadtile3\');' in browser.contents
    assert 'AdController.render(\'iqadtile7\');' in browser.contents


def test_adcontroller_finanlizer_is_present(testserver, testbrowser):
    browser = testbrowser('%s/zeit-online/index' % testserver.url)
    if not is_adcontrolled(browser.contents):
        pytest.skip("not applicable due to oldschool ad configuration")

    assert 'AdController.finalize();' in browser.contents
