# -*- coding: utf-8 -*-
import zeit.web.site.view

import jwt
import zope.component


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
    head = testbrowser('/framebuilder?page_slice=html_head')
    assert not head.cssselect('body')

    upper_body = testbrowser('/framebuilder?page_slice=upper_body')
    assert not upper_body.cssselect('head')
    assert '<body' in upper_body.contents
    assert '</body>' not in upper_body.contents

    lower_body = testbrowser('/framebuilder?page_slice=lower_body')
    assert not lower_body.cssselect('head')
    assert '<body' not in lower_body.contents
    assert '</body>' in lower_body.contents


def test_framebuilder_contains_no_webtrekk(testbrowser):
    browser = testbrowser('/framebuilder')
    assert 'webtrekk' not in browser.contents


def test_framebuilder_can_contain_webtrekk(testbrowser, togglepatch):
    togglepatch({'third_party_modules': True})
    browser = testbrowser('/framebuilder?webtrekk')
    webtrekk_script = browser.cssselect(
        'script[src^="https://scripts.zeit.de/static/js/webtrekk/"]')
    assert len(webtrekk_script) == 1


def test_framebuilder_sets_webtrekk_values_differently(
        testbrowser, togglepatch):
    togglepatch({'third_party_modules': True})
    browser = testbrowser('/framebuilder?webtrekk')
    script = browser.cssselect(
        'script[src*="/static/js/webtrekk/webtrekk"] + script')[0]
    webtrekk_config = script.text_content().strip()

    assert ('wt.contentId = "redaktion....centerpage.zede|" + '
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
        'script[src="//s62.mxcdn.net/bb-serve/mtrcs_225560.js"]')
    assert len(meetrics_script) == 0


def test_framebuilder_can_contain_meetrics(testbrowser, togglepatch):
    togglepatch({'third_party_modules': True})
    browser = testbrowser('/framebuilder?meetrics')
    meetrics_script = browser.cssselect(
        'script[src="//s62.mxcdn.net/bb-serve/mtrcs_225560.js"]')
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
    assert 'homepage_trsf' == driver.execute_script(
        'return adcSiteInfo.$handle')
    assert 'one' == driver.execute_script('return adcSiteInfo.level2')
    assert 'two' == driver.execute_script('return adcSiteInfo.level3')
    assert 'three' == driver.execute_script('return adcSiteInfo.level4')
    assert '' == driver.execute_script('return adcSiteInfo.keywords')

    driver.get('{}/framebuilder?banner_channel={}'.format(
        testserver.url, 'oans/zwoa//index'))
    assert 'index_trsf' == driver.execute_script('return adcSiteInfo.$handle')
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
    assert 'artikel_trsf' == driver.execute_script(
        'return adcSiteInfo.$handle')
    assert '' == driver.execute_script('return adcSiteInfo.level2')
    assert '' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')
    assert '' == driver.execute_script('return adcSiteInfo.keywords')

    driver.get('{}/framebuilder'.format(testserver.url))
    assert 'undefined' == driver.execute_script('return typeof adcSiteInfo')

    driver.get('{}/framebuilder?banner_channel={}'.format(
        testserver.url, 'one/two/three/four/my,keywords,in,channel'))
    assert 'four_trsf' == driver.execute_script('return adcSiteInfo.$handle')
    assert 'one' == driver.execute_script('return adcSiteInfo.level2')
    assert 'two' == driver.execute_script('return adcSiteInfo.level3')
    assert 'three' == driver.execute_script('return adcSiteInfo.level4')
    assert 'my,keywords,in,channel' == driver.execute_script(
        'return adcSiteInfo.keywords')

    driver.get('{}/framebuilder?banner_channel={}'.format(
        testserver.url, '///homepage/my,keywords'))
    assert 'homepage_trsf' == driver.execute_script(
        'return adcSiteInfo.$handle')
    assert '' == driver.execute_script('return adcSiteInfo.level2')
    assert '' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')
    assert 'my,keywords' == driver.execute_script(
        'return adcSiteInfo.keywords')


def test_framebuilder_minimal_should_slice_page_on_request(testbrowser):

    head = testbrowser('/framebuilder?minimal&page_slice=html_head')
    assert not head.cssselect('body')

    upper_body = testbrowser('/framebuilder?minimal&page_slice=upper_body')
    assert not upper_body.cssselect('head')
    assert '<body' in upper_body.contents
    assert '</body>' not in upper_body.contents

    lower_body = testbrowser('/framebuilder?minimal&page_slice=lower_body')
    assert not lower_body.cssselect('head')
    assert '<body' not in lower_body.contents
    assert '</body>' in lower_body.contents


def test_framebuilder_minimal_contains_no_webtrekk(testbrowser):
    browser = testbrowser('/framebuilder')
    assert 'webtrekk' not in browser.contents


def test_framebuilder_minimal_can_contain_webtrekk(testbrowser, togglepatch):
    togglepatch({'third_party_modules': True})
    browser = testbrowser('/framebuilder?minimal&webtrekk')
    webtrekk_script = browser.cssselect(
        'script[src^="https://scripts.zeit.de/static/js/webtrekk/"]')
    assert len(webtrekk_script) == 1


def test_framebuilder_minimal_sets_webtrekk_values_differently(
        testbrowser, togglepatch):
    togglepatch({'third_party_modules': True})
    browser = testbrowser('/framebuilder?minimal&webtrekk')
    assert ('wt.contentId = "redaktion....centerpage.zede|" + '
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
    assert 'homepage_trsf' == driver.execute_script(
        'return adcSiteInfo.$handle')
    assert 'one' == driver.execute_script('return adcSiteInfo.level2')
    assert 'two' == driver.execute_script('return adcSiteInfo.level3')
    assert 'three' == driver.execute_script('return adcSiteInfo.level4')
    assert '' == driver.execute_script('return adcSiteInfo.keywords')

    driver.get('{}/framebuilder?minimal&banner_channel={}'.format(
        testserver.url, 'oans/zwoa//index'))
    assert 'index_trsf' == driver.execute_script('return adcSiteInfo.$handle')
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
    assert 'artikel_trsf' == driver.execute_script(
        'return adcSiteInfo.$handle')
    assert '' == driver.execute_script('return adcSiteInfo.level2')
    assert '' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')
    assert '' == driver.execute_script('return adcSiteInfo.keywords')

    driver.get('{}/framebuilder?minimal'.format(testserver.url))
    assert 'undefined' == driver.execute_script('return typeof adcSiteInfo')

    driver.get('{}/framebuilder?minimal&banner_channel={}'.format(
        testserver.url, 'one/two/three/four/my,keywords,in,channel'))
    assert 'four_trsf' == driver.execute_script('return adcSiteInfo.$handle')
    assert 'one' == driver.execute_script('return adcSiteInfo.level2')
    assert 'two' == driver.execute_script('return adcSiteInfo.level3')
    assert 'three' == driver.execute_script('return adcSiteInfo.level4')
    assert 'my,keywords,in,channel' == driver.execute_script(
        'return adcSiteInfo.keywords')

    driver.get('{}/framebuilder?minimal&banner_channel={}'.format(
        testserver.url, '///homepage/my,keywords'))
    assert 'homepage_trsf' == driver.execute_script(
        'return adcSiteInfo.$handle')
    assert '' == driver.execute_script('return adcSiteInfo.level2')
    assert '' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')
    assert 'my,keywords' == driver.execute_script(
        'return adcSiteInfo.keywords')


def test_framebuilder_loads_slimmed_script_file(testbrowser):
    browser = testbrowser('/framebuilder')
    scripts = browser.cssselect('body script')
    assert scripts[-1].get('src').endswith('/js/web.site/frame.js')


def test_framebuilder_should_require_ssl(application, dummy_request):
    dummy_request.GET['useSSL'] = 'true'
    view = zeit.web.site.view.FrameBuilder(None, dummy_request)

    assert view.framebuilder_requires_ssl is True


def test_framebuilder_uses_ssl_assets(testbrowser):
    browser = testbrowser('/framebuilder?useSSL')
    ssl_str = 'https://ssl.zeit.de/www.zeit.de/static/latest/'
    assert '{}css/web.site/framebuilder.css'.format(
        ssl_str) in browser.contents
    assert '{}js/vendor/modernizr-custom.js'.format(
        ssl_str) in browser.contents
    assert '{}js/web.site/frame.js'.format(ssl_str) in browser.contents


# needs selenium because of esi include
def test_framebuilder_does_not_render_login_data(
        selenium_driver, testserver, sso_keypair):
    driver = selenium_driver
    select = driver.find_elements_by_css_selector

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['sso_key'] = sso_keypair['public']
    sso_cookie = jwt.encode(
        {'id': 'ssoid'}, sso_keypair['private'], 'RS256')

    # add_cookie() only works for the domain of the last get(), sigh.
    driver.get('{}/zeit-online/article/simple'.format(testserver.url))
    driver.add_cookie({'name': 'my_sso_cookie', 'value': sso_cookie})

    driver.get('{}/zeit-online/article/simple'.format(testserver.url))
    assert len(select('.nav__user-name')) == 1

    # 'my_sso_cookie' is a dummy cookie an does not trigger the JS DOM
    # manipulation injecting the login data.
    # We test, if user data is not exposed in actual frambuilder source HTML.
    # We just can't do anything about it if someone copies interpreted frame
    # HTML from DevTools - well, we could, but we won't for now.
    driver.get('{}/framebuilder'.format(testserver.url))
    assert len(select('.nav__user-name')) == 0


def test_framebuilder_renders_login_data(
        selenium_driver, testserver, sso_keypair):
    driver = selenium_driver
    select = driver.find_elements_by_css_selector

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['sso_key'] = sso_keypair['public']
    sso_cookie = jwt.encode(
        {'id': 'ssoid'}, sso_keypair['private'], 'RS256')

    # add_cookie() only works for the domain of the last get(), sigh.
    driver.get('{}/zeit-online/article/simple'.format(testserver.url))
    driver.add_cookie({'name': 'zeit_sso_201501', 'value': sso_cookie})

    # 'zeit_sso_201501' is the actual real-life Cookie
    # login-data is displayed
    driver.get('{}/framebuilder'.format(testserver.url))
    assert len(select('.nav__user-name')) == 1

    # ... and test if the featuretoggle is set if requested
    assert len(select('.nav__login')) == 1
    assert not select('.nav__login')[0].get_attribute('data-featuretoggle')
    driver.get('{}/framebuilder?loginstatus_disabled'.format(testserver.url))
    assert select('.nav__login')[0].get_attribute(
        'data-featuretoggle') == 'disable-loginstatus'
    assert len(select('.nav__user-name')) == 0


def test_framebuilder_renders_login_data_if_new_feature_is_requested(
        selenium_driver, togglepatch, testserver, sso_keypair):
    togglepatch({'framebuilder_loginstatus_disabled': True})
    driver = selenium_driver
    select = driver.find_elements_by_css_selector

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['sso_key'] = sso_keypair['public']
    sso_cookie = jwt.encode(
        {'id': 'ssoid'}, sso_keypair['private'], 'RS256')

    # add_cookie() only works for the domain of the last get(), sigh.
    driver.get('{}/zeit-online/article/simple'.format(testserver.url))
    driver.add_cookie({'name': 'zeit_sso_201501', 'value': sso_cookie})

    # ... and set if it can be enforced, even if disabled in feature toggles
    driver.get('{}/framebuilder?loginstatus_enforced'.format(testserver.url))
    assert len(select('.nav__login')) == 1
    assert not select('.nav__login')[0].get_attribute('data-featuretoggle')
    assert len(select('.nav__user-name')) == 1
