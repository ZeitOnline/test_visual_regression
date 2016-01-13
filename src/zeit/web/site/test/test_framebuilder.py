# -*- coding: utf-8 -*-
import zeit.web.site.view


def test_framebuilder_should_set_ressort(application, dummy_request):
    dummy_request.GET['ressort'] = 'kultur'
    view = zeit.web.site.view.FrameBuilder(None, dummy_request)
    assert view.ressort == 'kultur'


def test_framebuilder_should_set_banner_channel(application, dummy_request):
    dummy_request.GET['banner_channel'] = 'digital/centerpage'
    view = zeit.web.site.view.FrameBuilder(None, dummy_request)

    assert view.advertising_enabled is True
    assert view.banner_channel == 'digital/centerpage'


def test_framebuilder_can_disable_responsiveness(testbrowser):
    browser = testbrowser('/framebuilder?desktop_only=true')
    assert 'unresponsive.css' in browser.contents
    assert 'screen.css' not in browser.contents


def test_framebuilder_should_slice_page_on_request(testbrowser):
    full_page = testbrowser('/framebuilder')

    head = testbrowser('/framebuilder?page_slice=html_head')
    assert not head.cssselect('body')
    assert head.contents in full_page.contents

    upper_body = testbrowser('/framebuilder?page_slice=upper_body')
    assert not upper_body.cssselect('head')

    sanitized = upper_body.contents.replace(
        '?page_slice=upper_body', '').strip()
    assert '</body>' not in sanitized
    assert sanitized in full_page.contents

    lower_body = testbrowser('/framebuilder?page_slice=lower_body')
    assert not lower_body.cssselect('head')
    assert '</body>' in lower_body.contents
    assert lower_body.contents.strip() in full_page.contents


def test_framebuilder_contains_webtrekk(testbrowser):
    browser = testbrowser('/framebuilder')
    webtrekk_script = browser.cssselect(
        'script[src^="http://scripts.zeit.de/static/js/webtrekk/"]')
    assert len(webtrekk_script) == 1


def test_framebuilder_can_disable_webtrekk(testbrowser):
    browser = testbrowser('/framebuilder?webtrekk_disabled')
    webtrekk_script = browser.cssselect(
        'script[src^="http://scripts.zeit.de/static/js/webtrekk/"]')
    assert len(webtrekk_script) == 0
