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
    full_page = testbrowser('/framebuilder').contents

    head = testbrowser('/framebuilder?page_slice=html_head').contents
    assert not testbrowser.cssselect('body')
    assert head in full_page

    upper_body = testbrowser('/framebuilder?page_slice=upper_body').contents
    assert not testbrowser.cssselect('head')

    sanitized = upper_body.replace('?page_slice=upper_body', '').strip()
    assert '</body>' not in sanitized
    assert sanitized in full_page

    lower_body = testbrowser('/framebuilder?page_slice=lower_body').contents
    assert not testbrowser.cssselect('head')
    assert '</body>' in lower_body
    assert lower_body.strip() in full_page


def test_framebuilder_contains_no_webtrekk(testbrowser):
    browser = testbrowser('/framebuilder')
    assert 'webtrekk' not in browser.contents


def test_framebuilder_can_contain_webtrekk(testbrowser):
    browser = testbrowser('/framebuilder?webtrekk')
    webtrekk_script = browser.cssselect(
        'script[src^="http://scripts.zeit.de/static/js/webtrekk/"]')
    assert len(webtrekk_script) == 1


def test_framebuilder_sets_webtrekk_values_differently(testbrowser):
    browser = testbrowser('/framebuilder?webtrekk')
    script = browser.cssselect(
        'script[src*="/static/js/webtrekk/webtrekk"] + script')[0]
    webtrekk_config = script.text_content().strip()

    assert ('var Z_WT_KENNUNG = "redaktion....centerpage.zede|" + '
            'window.location.hostname + '
            'window.location.pathname;') in webtrekk_config
    assert ("7: window.location.pathname.split('/').pop()") in webtrekk_config
    assert '26: "centerpage.framebuilder"' in webtrekk_config


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


def test_framebuilder_contains_no_meetrics(testbrowser):
    browser = testbrowser('/framebuilder')
    meetrics_script = browser.cssselect(
        'script[src="http://s62.mxcdn.net/bb-serve/mtrcs_225560.js"]')
    assert len(meetrics_script) == 0


def test_framebuilder_can_contain_meetrics(testbrowser):
    browser = testbrowser('/framebuilder?meetrics')
    meetrics_script = browser.cssselect(
        'script[src="http://s62.mxcdn.net/bb-serve/mtrcs_225560.js"]')
    assert len(meetrics_script) == 1


def test_framebuilder_should_show_ressort_nav_by_default(testbrowser):
    browser = testbrowser('/framebuilder')
    assert browser.cssselect('.nav__ressorts')


def test_framebuilder_can_disable_ressort(testbrowser):
    browser = testbrowser('/framebuilder?hide_ressorts')
    assert not browser.cssselect('.nav__ressorts')


def test_framebuilder_should_show_search_form_by_default(testbrowser):
    browser = testbrowser('/framebuilder')
    assert browser.cssselect('.nav .search')


def test_framebuilder_can_omit_search_form(testbrowser):
    browser = testbrowser('/framebuilder?hide_search')
    assert not browser.cssselect('.nav .search')


def test_framebuilder_displays_no_adlabel_by_default(testbrowser):
    browser = testbrowser('/framebuilder')
    assert 'ad-label' not in browser.contents  # desktop
    assert 'advertorial-marker' not in browser.contents  # mobile


def test_framebuilder_displays_adlabel_if_requested(testbrowser):
    browser = testbrowser('/framebuilder?adlabel=sch%C3%B6nes%20Wurstbrot')
    # desktop:
    adlabel = browser.cssselect('.header__ad-label')
    assert len(adlabel) == 1
    assert adlabel[0].text.strip() == u'schönes Wurstbrot'
    # mobile:
    adlabel = browser.cssselect('.advertorial-marker__label')
    assert len(adlabel) == 1
    assert adlabel[0].text.strip() == u'schönes Wurstbrot'


def test_framebuilder_should_have_login_cut_mark(testbrowser):
    browser = testbrowser('/framebuilder')
    assert 'start::cut_mark::login' in browser.contents
    assert 'end::cut_mark::login' in browser.contents


def test_framebuilder_accepts_banner_channel_parameter(
        selenium_driver, testserver, monkeypatch):

    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True, 'iqd': True}.get)
    driver = selenium_driver

    # avoid "diuquilon", which is added by JS for specific screen sizes
    driver.set_window_size(1200, 800)

    driver.get('{}/framebuilder?banner_channel={}'.format(
        testserver.url, 'one/two/three/homepage'))
    assert 'homepage' == driver.execute_script('return adcSiteInfo.$handle')
    assert 'one' == driver.execute_script('return adcSiteInfo.level2')
    assert 'two' == driver.execute_script('return adcSiteInfo.level3')
    assert 'three' == driver.execute_script('return adcSiteInfo.level4')
    assert '' == driver.execute_script('return adcSiteInfo.keywords')

    driver.get('{}/framebuilder?banner_channel={}'.format(
        testserver.url, 'oans/zwoa//index'))
    assert 'index' == driver.execute_script('return adcSiteInfo.$handle')
    assert 'oans' == driver.execute_script('return adcSiteInfo.level2')
    assert 'zwoa' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')
    assert '' == driver.execute_script('return adcSiteInfo.keywords')

    driver.get('{}/framebuilder?banner_channel={}'.format(
        testserver.url, 'eins'))
    assert '' == driver.execute_script('return adcSiteInfo.$handle')
    assert 'eins' == driver.execute_script('return adcSiteInfo.level2')
    assert '' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')
    assert '' == driver.execute_script('return adcSiteInfo.keywords')

    driver.get('{}/framebuilder?banner_channel={}'.format(
        testserver.url, '///artikel'))
    assert 'artikel' == driver.execute_script('return adcSiteInfo.$handle')
    assert '' == driver.execute_script('return adcSiteInfo.level2')
    assert '' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')
    assert '' == driver.execute_script('return adcSiteInfo.keywords')

    driver.get('{}/framebuilder'.format(testserver.url))
    assert 'undefined' == driver.execute_script('return typeof adcSiteInfo')

    driver.get('{}/framebuilder?banner_channel={}'.format(
        testserver.url, 'one/two/three/four/my,keywords,in,channel'))
    assert 'four' == driver.execute_script('return adcSiteInfo.$handle')
    assert 'one' == driver.execute_script('return adcSiteInfo.level2')
    assert 'two' == driver.execute_script('return adcSiteInfo.level3')
    assert 'three' == driver.execute_script('return adcSiteInfo.level4')
    assert 'my,keywords,in,channel' == driver.execute_script(
        'return adcSiteInfo.keywords')

    driver.get('{}/framebuilder?banner_channel={}'.format(
        testserver.url, '///homepage/my,keywords'))
    assert 'homepage' == driver.execute_script('return adcSiteInfo.$handle')
    assert '' == driver.execute_script('return adcSiteInfo.level2')
    assert '' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')
    assert 'my,keywords' == driver.execute_script(
        'return adcSiteInfo.keywords')


# ----------- MINIMAL FRAMEBUILDER -----------------------------------------
def test_framebuilder_minimal_should_slice_page_on_request(testbrowser):
    full_page = testbrowser('/framebuilder?minimal').contents

    head = testbrowser('/framebuilder?minimal&page_slice=html_head').contents
    assert not testbrowser.cssselect('body')
    assert head in full_page

    upper_body = testbrowser(
        '/framebuilder?minimal&page_slice=upper_body').contents
    assert not testbrowser.cssselect('head')

    sanitized = upper_body.replace(
        '?minimal&page_slice=upper_body', '').strip()
    assert '</body>' not in sanitized
    assert sanitized in full_page

    lower_body = testbrowser(
        '/framebuilder?minimal&page_slice=lower_body').contents
    assert not testbrowser.cssselect('head')
    assert '</body>' in lower_body
    assert lower_body.strip() in full_page


def test_framebuilder_minimal_contains_no_webtrekk(testbrowser):
    browser = testbrowser('/framebuilder')
    assert 'webtrekk' not in browser.contents


def test_framebuilder_minimal_can_contain_webtrekk(testbrowser):
    browser = testbrowser('/framebuilder?minimal&webtrekk')
    webtrekk_script = browser.cssselect(
        'script[src^="http://scripts.zeit.de/static/js/webtrekk/"]')
    assert len(webtrekk_script) == 1


def test_framebuilder_minimal_sets_webtrekk_values_differently(testbrowser):
    browser = testbrowser('/framebuilder?minimal&webtrekk')
    assert ('var Z_WT_KENNUNG = "redaktion....centerpage.zede|" + '
            'window.location.hostname + '
            'window.location.pathname;') in browser.contents
    assert ("7: window.location.pathname.split('/').pop()") in browser.contents
    assert '26: "centerpage.framebuilder"' in browser.contents


def test_framebuilder_minimal_contains_no_ivw(testbrowser):
    browser = testbrowser('/framebuilder?minimal')
    assert 'iam.js' not in browser.contents
    assert 'iam_data' not in browser.contents


def test_framebuilder_minimal_can_contain_ivw(testbrowser):
    browser = testbrowser('/framebuilder?minimal&ivw')
    ivw_script = browser.cssselect(
        'script[src="https://script.ioam.de/iam.js"]')
    assert len(ivw_script) == 1
    assert 'var iam_data = {' in browser.contents


def test_framebuilder_contains_data_for_wrapper_app(testbrowser):
    browser = testbrowser('/framebuilder')
    assert 'window.wrapper' in browser.contents
    assert ("isWrapped: navigator.userAgent.indexOf('ZONApp') > -1,"
            in browser.cssselect('head')[0].text_content())


# TODO
def test_framebuilder_minimal_should_have_login_cut_mark(testbrowser):
    browser = testbrowser('/framebuilder')
    assert 'start::cut_mark::login' in browser.contents
    assert 'end::cut_mark::login' in browser.contents


def test_framebuilder_minimal_accepts_banner_channel_parameter(
        selenium_driver, testserver, monkeypatch):

    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True, 'iqd': True}.get)
    driver = selenium_driver

    # avoid "diuquilon", which is added by JS for specific screen sizes
    driver.set_window_size(1200, 800)

    driver.get('{}/framebuilder?minimal&banner_channel={}'.format(
        testserver.url, 'one/two/three/homepage'))
    assert 'homepage' == driver.execute_script('return adcSiteInfo.$handle')
    assert 'one' == driver.execute_script('return adcSiteInfo.level2')
    assert 'two' == driver.execute_script('return adcSiteInfo.level3')
    assert 'three' == driver.execute_script('return adcSiteInfo.level4')
    assert '' == driver.execute_script('return adcSiteInfo.keywords')

    driver.get('{}/framebuilder?minimal&banner_channel={}'.format(
        testserver.url, 'oans/zwoa//index'))
    assert 'index' == driver.execute_script('return adcSiteInfo.$handle')
    assert 'oans' == driver.execute_script('return adcSiteInfo.level2')
    assert 'zwoa' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')
    assert '' == driver.execute_script('return adcSiteInfo.keywords')

    driver.get('{}/framebuilder?minimal&banner_channel={}'.format(
        testserver.url, 'eins'))
    assert '' == driver.execute_script('return adcSiteInfo.$handle')
    assert 'eins' == driver.execute_script('return adcSiteInfo.level2')
    assert '' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')
    assert '' == driver.execute_script('return adcSiteInfo.keywords')

    driver.get('{}/framebuilder?minimal&banner_channel={}'.format(
        testserver.url, '///artikel'))
    assert 'artikel' == driver.execute_script('return adcSiteInfo.$handle')
    assert '' == driver.execute_script('return adcSiteInfo.level2')
    assert '' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')
    assert '' == driver.execute_script('return adcSiteInfo.keywords')

    driver.get('{}/framebuilder?minimal'.format(testserver.url))
    assert 'undefined' == driver.execute_script('return typeof adcSiteInfo')

    driver.get('{}/framebuilder?minimal&banner_channel={}'.format(
        testserver.url, 'one/two/three/four/my,keywords,in,channel'))
    assert 'four' == driver.execute_script('return adcSiteInfo.$handle')
    assert 'one' == driver.execute_script('return adcSiteInfo.level2')
    assert 'two' == driver.execute_script('return adcSiteInfo.level3')
    assert 'three' == driver.execute_script('return adcSiteInfo.level4')
    assert 'my,keywords,in,channel' == driver.execute_script(
        'return adcSiteInfo.keywords')

    driver.get('{}/framebuilder?minimal&banner_channel={}'.format(
        testserver.url, '///homepage/my,keywords'))
    assert 'homepage' == driver.execute_script('return adcSiteInfo.$handle')
    assert '' == driver.execute_script('return adcSiteInfo.level2')
    assert '' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')
    assert 'my,keywords' == driver.execute_script(
        'return adcSiteInfo.keywords')


def test_framebuilder_loads_slimmed_script_file(testbrowser):
    browser = testbrowser('/framebuilder')
    scripts = browser.cssselect('body script')
    assert scripts[-1].get('src').endswith('/js/web.site/frame.js')
