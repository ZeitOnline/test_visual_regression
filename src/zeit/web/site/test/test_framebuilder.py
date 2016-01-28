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
    browser = testbrowser('/framebuilder?desktop_only')
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


def test_framebuilder_contains_no_webtrekk(testbrowser):
    browser = testbrowser('/framebuilder')
    assert 'webtrekk' not in browser.contents


def test_framebuilder_can_contain_webtrekk(testbrowser):
    browser = testbrowser('/framebuilder?webtrekk')
    webtrekk_script = browser.cssselect(
        'script[src^="http://scripts.zeit.de/static/js/webtrekk/"]')
    assert len(webtrekk_script) == 1


def test_framebuilder_contains_no_ivw(testbrowser):
    browser = testbrowser('/framebuilder')
    assert 'iam.js' not in browser.contents
    assert 'iam_data' not in browser.contents


def test_framebuilder_can_contain_ivw(testbrowser):
    browser = testbrowser('/framebuilder?ivw')
    ivw_script = browser.cssselect(
        'script[src="https://script.ioam.de/iam.js"]')
    assert len(ivw_script) == 1
    assert 'var iam_data = {' in browser.contents


def test_framebuilder_should_inline_svgs(testbrowser):
    browser = testbrowser('/framebuilder')
    assert len(browser.xpath('/html/head/svg/symbol')) == 4
    assert browser.cssselect('.logo_bar svg > use')[0].attrib['xlink:href']
