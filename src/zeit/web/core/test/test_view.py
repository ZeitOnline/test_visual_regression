# -*- coding: utf-8 -*-
import mock
import pytest
import requests
import urllib2

import pyramid.request
import zope.component

import zeit.cms.tagging.testing

import zeit.web.core.application
import zeit.web.core.interfaces
import zeit.web.magazin.view
import zeit.web.magazin.view_article
import zeit.web.magazin.view_centerpage
import zeit.web.site.view_article
import zeit.web.site.view_author
import zeit.web.site.view_centerpage

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


def test_http_header_should_contain_c1_header_fields(testserver):
    assert requests.head(testserver.url + '/zeit-magazin/index').headers.get(
        'C1-Track-Doc-Type') == 'centerpage'


def test_c1_channel_should_correspond_to_context_ressort(
        application, dummy_request):

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/simple')
    view = zeit.web.core.view.Content(context, dummy_request)
    assert dict(view.c1_header).get('C1-Track-Channel') == 'sport'
    assert dict(view.c1_client).get('set_channel') == '"sport"'


def test_c1_channel_should_correspond_to_context_sub_ressort(
        application, dummy_request):

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/01')
    view = zeit.web.core.view.Content(context, dummy_request)
    assert dict(view.c1_header).get('C1-Track-Sub-Channel') == 'mode-design'
    assert dict(view.c1_client).get('set_sub_channel') == '"mode-design"'


def test_c1_cms_id_should_correspond_to_context_uuid(
        application, dummy_request):

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/simple')
    uuid = '{urn:uuid:85c42592-3840-41c6-b039-83cc16de66d6}'
    view = zeit.web.core.view.Content(context, dummy_request)
    assert dict(view.c1_header).get('C1-Track-CMS-ID') == uuid
    assert dict(view.c1_client).get('set_cms_id') == '"%s"' % uuid


def test_c1_content_id_should_correspond_to_webtrekk_content_id(
        application, dummy_request):
    zeit.web.core.application.FEATURE_TOGGLES.set(
        'tracking', 'iqd', 'third_party_modules')

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    view = zeit.web.core.view.Content(context, dummy_request)
    content_id = view.webtrekk_content_id
    assert dict(view.c1_header).get('C1-Track-Content-ID') == content_id
    assert dict(view.c1_client).get('set_content_id') == '"%s"' % content_id


@pytest.mark.parametrize('path, doc_type', [
    ('/zeit-online/parquet-teaser-setup', 'centerpage'),
    ('/zeit-online/gallery/biga_1', 'bildergalerie'),
    ('/framebuilder?page_slice=html_head', 'arena')])
def test_c1_doc_type_should_be_properly_mapped_to_context_type(
        testserver, path, doc_type):
    url = testserver.url + path
    assert requests.head(url).headers.get('C1-Track-Doc-Type') == doc_type


def test_c1_doc_type_should_be_included_in_cre_client(
        application, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/parquet-teaser-setup')
    view = zeit.web.core.view.Content(context, dummy_request)
    assert dict(view.c1_client).get('set_doc_type') == '"centerpage"'


def test_c1_heading_and_kicker_should_be_properly_escaped(
        application, dummy_request):

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/04')
    view = zeit.web.core.view.Content(context, dummy_request)
    assert dict(view.c1_header).get('C1-Track-Heading') == (
        u'Kann Leipzig Hypezig berleben?')
    assert dict(view.c1_client).get('set_heading') == (
        u'"Kann Leipzig Hypezig überleben?"')
    assert dict(view.c1_header).get('C1-Track-Kicker') == 'Szene-Stadt'
    assert dict(view.c1_client).get('set_kicker') == '"Szene-Stadt"'


def test_c1_headers_should_be_properly_escaped(application, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/04')
    view = zeit.web.core.view.Content(context, dummy_request)
    with mock.patch('zeit.web.core.paywall.CeleraOneMixin._c1_channel',
                    mock.PropertyMock()) as channel:
        channel.return_value = 'foo\nbar'
        assert dict(view.c1_header).get('C1-Track-Channel') == 'foobar'


def test_c1_service_id_should_be_included_in_tracking_parameters(
        application, dummy_request):

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/simple')
    view = zeit.web.core.view.Content(context, dummy_request)
    assert dict(view.c1_header).get('C1-Track-Service-ID') == 'zon'
    assert dict(view.c1_client).get('set_service_id') == '"zon"'


def test_c1_origin_should_trigger_js_call_for_cre_client(
        testbrowser, dummy_request):
    zeit.web.core.application.FEATURE_TOGGLES.set(
        'tracking', 'iqd', 'third_party_modules')
    browser = testbrowser('/zeit-online/article/simple')
    assert 'cre_client.set_origin( window.Zeit.getCeleraOneOrigin() );' in (
        browser.contents)


def test_text_file_content_should_be_rendered(testbrowser):
    browser = testbrowser('/text/dummy')
    assert browser.contents == 'zeit.web\n'


def test_c1_include_script_gets_appended(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set(
        'tracking', 'third_party_modules')
    browser = testbrowser('/zeit-online/article/simple')
    inline = u''.join(browser.xpath('//script/text()'))
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    assert 'script.src = "{}/tracking/tracking.js"'.format(
        conf.get('c1_prefix')) in inline


def test_c1_correct_ressort_on_homepage(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set(
        'tracking', 'iqd', 'third_party_modules')
    browser = testbrowser('/zeit-online/slenderized-index')
    assert 'cre_client.set_channel( "homepage" );' in (browser.contents)


def test_c1_client_should_receive_entitlement(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('tracking')
    access_source = zeit.cms.content.sources.ACCESS_SOURCE.factory
    assert 'cre_client.set_entitlement( "{}" );'.format(
        access_source.translate_to_c1('free')) in (
            testbrowser('/zeit-online/article/01').contents)
    assert 'cre_client.set_entitlement( "{}" );'.format(
        access_source.translate_to_c1('registration')) in (
            testbrowser('zeit-online/article/zplus-zeit-register').contents)
    assert 'cre_client.set_entitlement( "{}" );'.format(
        access_source.translate_to_c1('abo')) in (
            testbrowser('zeit-online/article/zplus-zeit').contents)


def test_http_header_should_contain_c1_entitlement(testserver):
    zeit.web.core.application.FEATURE_TOGGLES.set('tracking')
    access_source = zeit.cms.content.sources.ACCESS_SOURCE.factory
    assert requests.head(
        testserver.url + '/zeit-online/article/01').headers.get(
            'C1-Track-Entitlement') == access_source.translate_to_c1('free')
    register_article = (
        testserver.url + '/zeit-online/article/zplus-zeit-register')
    assert requests.head(register_article).headers.get(
        'C1-Track-Entitlement') == (
            access_source.translate_to_c1('registration'))
    assert requests.head(
        testserver.url + '/zeit-online/article/zplus-zeit').headers.get(
            'C1-Track-Entitlement') == access_source.translate_to_c1('abo')


def test_http_header_should_contain_c1_entitlement_id(testserver):
    zeit.web.core.application.FEATURE_TOGGLES.set('tracking')

    free_article = testserver.url + '/zeit-online/article/01'
    assert not requests.head(free_article).headers.get(
        'C1-Track-Entitlement-ID')

    register_article = (
        testserver.url + '/zeit-online/article/zplus-zeit-register')
    assert requests.head(register_article).headers.get(
        'C1-Track-Entitlement-ID') == 'zeit-fullaccess'

    paid_article = testserver.url + '/zeit-online/article/zplus-zeit'
    assert requests.head(paid_article).headers.get(
        'C1-Track-Entitlement-ID') == 'zeit-fullaccess'


def test_inline_gallery_should_be_contained_in_body(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/01')
    assert isinstance(
        context.body.values()[-1], zeit.content.article.edit.reference.Gallery)


def test_inline_gallery_should_have_images(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/01')
    gallery = zeit.web.core.interfaces.IArticleModule(
        context.body.values()[-1])
    image = zeit.web.core.template.get_image(list(gallery)[5])
    assert image.path == (
        '/galerien/bg-automesse-detroit-2014-usa-bilder'
        '/chrysler%20200%20s%201-540x304.jpg/imagegroup/original')
    assert image.alt is None
    assert image.copyrights == ()


def test_breaking_news_should_be_provided(application):
    view = zeit.web.core.view.Base(None, None)
    assert zeit.web.core.interfaces.IBreakingNews.providedBy(
        view.breaking_news)


def test_unpublished_breaking_news_should_be_detected(application):
    view = zeit.web.core.view.Base(None, None)
    assert view.breaking_news.published is False


def test_published_breaking_news_should_be_detected(application, monkeypatch):
    monkeypatch.setattr(
        zeit.workflow.workflow.ContentWorkflow, 'published', True)
    view = zeit.web.core.view.Base(None, None)
    assert view.breaking_news.published is True


def test_missing_breaking_news_should_eval_to_false(application):
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    settings['breaking_news'] = 'moep'
    view = zeit.web.core.view.Base(None, None)
    assert view.breaking_news.published is False


def test_centerpage_should_have_manual_seo_pagetitle(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/centerpage/index')
    view = zeit.web.magazin.view_centerpage.Centerpage(
        context, pyramid.testing.DummyRequest())
    assert view.pagetitle == u'ZMO CP: ZMO | ZEITmagazin'


def test_centerpage_should_have_generated_seo_pagetitle(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/centerpage/index')
    view = zeit.web.magazin.view_centerpage.Centerpage(
        context, pyramid.testing.DummyRequest())
    assert view.pagetitle == u'ZMO CP: ZMO | ZEITmagazin'


def test_centerpage_should_have_subtitle_seo_pagedesciption(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp-legacy/index')
    view = zeit.web.magazin.view_centerpage.Centerpage(
        context, pyramid.testing.DummyRequest())
    assert 'My Test SEO - ZEITmagazin ONLINE' in view.pagedescription


def test_article_should_have_postfixed_seo_pagetitle(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/06')
    view = zeit.web.magazin.view_article.Article(
        context, pyramid.testing.DummyRequest())
    assert view.pagetitle == (u'Friedhof Hamburg-Ohlsdorf: '
                              'Im Schnabel des Graureihers | ZEITmagazin')


def test_homepage_should_have_unpostfixed_seo_pagetitle(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index')
    view = zeit.web.site.view_centerpage.Centerpage(
        context, pyramid.testing.DummyRequest())
    assert view.pagetitle == u'ZON title'


def test_centerpage_should_have_manual_seo_pagedescription(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp-legacy/index')
    view = zeit.web.magazin.view_centerpage.Centerpage(
        context, pyramid.testing.DummyRequest())
    assert view.pagedescription == (u'My Test SEO - ZEITmagazin ONLINE ist '
                                    'die emotionale Seite von ZEIT ONLINE.')


def test_centerpage_should_have_default_seo_pagedescription(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/index')
    view = zeit.web.magazin.view_centerpage.Centerpage(
        context, pyramid.testing.DummyRequest())
    assert view.pagedescription == zeit.web.magazin.view.Base.seo_title_default


def test_notfound_view_works_for_get(testbrowser):
    browser = testbrowser()
    with pytest.raises(urllib2.HTTPError) as err:
        browser.open('/nonexistent')
    assert err.value.getcode() == 404


def test_notfound_view_works_for_post(testbrowser):
    browser = testbrowser()
    with pytest.raises(urllib2.HTTPError) as err:
        browser.post('/nonexistent', data='')
    assert err.value.getcode() == 404


def test_canonical_handles_non_ascii_urls(application):
    req = pyramid.request.Request.blank(u'/ümläut'.encode('utf-8'))
    req.registry = application.zeit_app.config.registry
    view = zeit.web.core.view.Base(None, req)
    assert u'http://localhost/ümläut' == view.canonical_url


def test_unavailable_handles_broken_unicode():
    req = pyramid.request.Request.blank('/%14%85')
    view = zeit.web.core.view.service_unavailable(None, req)
    # assert nothing raised:
    view()


def test_og_url_is_set_correctly(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index')
    request = pyramid.testing.DummyRequest(route_url=lambda x: 'foo/')
    view = zeit.web.site.view_centerpage.Centerpage(context, request)
    view.request.traversed = ('politik', 'index')
    assert view.og_url == 'foo/politik/index'


def test_wrapped_page_has_wrapped_property(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/slenderized-index')
    request = pyramid.testing.DummyRequest(headers={
        'user-agent': 'Safari/537.36 ZONApp/Android/2.3beta'})
    request.host_url = 'http://www.zeit.de'
    view = zeit.web.site.view_centerpage.Centerpage(context, request)
    assert view.is_wrapped

    request = pyramid.testing.DummyRequest(headers={
        'user-agent': 'Safari/537.36'})
    request.query_string = "app-content"
    request.host_url = 'http://www.zeit.de'
    view = zeit.web.site.view_centerpage.Centerpage(context, request)
    assert view.is_wrapped


def test_trailing_slash_should_lead_to_redirect():
    request = pyramid.testing.DummyRequest()
    request.path = '/foo/baa/'
    request.url = 'http://foo.xyz.de/foo/baa/?batz'
    with pytest.raises(
            pyramid.httpexceptions.HTTPMovedPermanently) as redirect:
        zeit.web.core.view.redirect_on_trailing_slash(request)

    assert redirect.value.location == 'http://foo.xyz.de/foo/baa?batz'

    request.path = '/foo/baa/'
    request.url = 'http://foo.xyz.de/foo/baa/'

    with pytest.raises(
            pyramid.httpexceptions.HTTPMovedPermanently) as redirect:
        zeit.web.core.view.redirect_on_trailing_slash(request)

    assert redirect.value.location == 'http://foo.xyz.de/foo/baa'

    request.path = '/foo/baa'
    request.url = 'http://foo.xyz.de/foo/baa'
    assert zeit.web.core.view.redirect_on_trailing_slash(request) is None


def test_ispaginated_predicate_should_handle_get_parameter():
    ip = zeit.web.core.view.is_paginated
    assert ip(None, mock.Mock(GET={})) is False
    assert ip(None, mock.Mock(GET={'p': 'klaus'})) is False
    assert ip(None, mock.Mock(GET={'p': '1'})) is False
    assert ip(None, mock.Mock(GET={'p': '4'})) is True


def test_invalid_unicode_should_return_http_400(testserver):
    r = requests.get(testserver.url + '/index%C8')
    assert r.status_code == 400


def test_ivw_uses_hyprid_method_for_apps(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.core:templates/inc/tracking/ivw_ver2.html')
    view = mock.Mock()
    view.is_wrapped = True
    html = tpl.render(view=mock.Mock(), request=mock.Mock())
    assert 'iom.h' in html
    assert 'iom.c' not in html


def test_amp_article_should_have_amp_link(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/zeit')
    view = zeit.web.site.view_article.Article(
        context, pyramid.testing.DummyRequest())
    assert view.is_amp


def test_rawr_config_should_exist_on_article_page(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/campus/article/simple_date_changed' % testserver.url)

    assert '/campus/article/simple_date_changed' == driver.execute_script(
        "return rawrConfig.locationMetaData.article_id")
    assert '/campus/article/simple_date_changed' == driver.execute_script(
        "return rawrConfig.locationMetaData.ident")
    assert '2016-02-10T10:39:16+01:00' == driver.execute_script(
        "return rawrConfig.locationMetaData.published")
    assert 'Hier gibt es Hilfe' == driver.execute_script(
        "return rawrConfig.locationMetaData.description")
    assert ['Studium', 'Uni-Leben'] == driver.execute_script(
        "return rawrConfig.locationMetaData.channels")
    assert ['studium', 'uni-leben'] == driver.execute_script(
        "return rawrConfig.locationMetaData.ressorts")
    tags = driver.execute_script(
        "return rawrConfig.locationMetaData.tags")
    assert tags[0] == 'Student'
    assert tags[3] == u'Bafög-Antrag'
    assert tags[5] == 'Studienfinanzierung'
    assert 'Hier gibt es Hilfe' == driver.execute_script(
        "return rawrConfig.locationMetaData.meta.description")


def test_rawr_config_should_have_series_tag(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/campus/article/02-beziehung-schluss-machen'
               % testserver.url)
    assert 'In der Mensa mit' == driver.execute_script(
        "return rawrConfig.locationMetaData.series")


def test_health_check_should_response_and_have_status_200(testbrowser):
    browser = testbrowser('/health-check')
    assert browser.headers['Content-Length'] == '2'
    resp = zeit.web.core.view.health_check('request')
    assert resp.status_code == 200


def test_health_check_should_fail_if_repository_does_not_exist(testbrowser):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['vivi_zeit.connector_repository-path'] = '/i_do_not_exist'

    with pytest.raises(pyramid.httpexceptions.HTTPInternalServerError):
        zeit.web.core.view.health_check('request')


def test_health_check_with_fs_should_be_configurable(testbrowser):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['vivi_zeit.connector_repository-path'] = '/i_do_not_exist'
    conf['health_check_with_fs'] = False

    resp = zeit.web.core.view.health_check('request')
    assert resp.status_code == 200

    conf['health_check_with_fs'] = True
    with pytest.raises(pyramid.httpexceptions.HTTPInternalServerError):
        zeit.web.core.view.health_check('request')


def test_reader_revenue_status_should_reflect_access_right(dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.webtrekk['customParameter']['cp28'] == 'free'

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/zplus-zeit-register')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.webtrekk['customParameter']['cp28'] == 'registration'

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/zplus-zeit')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.webtrekk['customParameter']['cp28'] == 'abo'


def test_jquery_not_overwritten(testserver, selenium_driver):
    script = 'return jQuery.fn.jquery'

    # ZON article
    selenium_driver.get(
        '{}/zeit-online/article/jquery-local-scope'.format(testserver.url))
    assert '2.2.4' == selenium_driver.execute_script(script)

    # ZMO article
    selenium_driver.get(
        '{}/zeit-magazin/article/jquery-local-scope'.format(testserver.url))
    assert '2.2.4' == selenium_driver.execute_script(script)

    # ZCO article
    selenium_driver.get(
        '{}/campus/article/jquery-local-scope'.format(testserver.url))
    assert '2.2.4' == selenium_driver.execute_script(script)


def test_jquery_not_in_window_scope(testserver, selenium_driver):
    script = 'return typeof window.jQuery'

    # ZON article
    selenium_driver.get('{}/zeit-online/article/simple'.format(testserver.url))
    assert 'undefined' == selenium_driver.execute_script(script)

    # ZMO article
    selenium_driver.get('{}/zeit-magazin/article/10'.format(testserver.url))
    assert 'undefined' == selenium_driver.execute_script(script)

    # ZCO article
    selenium_driver.get('{}/campus/article/simple'.format(testserver.url))
    assert 'undefined' == selenium_driver.execute_script(script)

    # ZON Framebuilder
    selenium_driver.get('{}/framebuilder'.format(testserver.url))
    assert 'undefined' == selenium_driver.execute_script(script)

    # ZCO Framebuilder
    selenium_driver.get('{}/campus/framebuilder'.format(testserver.url))
    assert 'undefined' == selenium_driver.execute_script(script)


def test_webtrekk_tracking_id_is_defined(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules')
    browser = testbrowser('/zeit-online/article/simple')
    assert 'window.webtrekkConfig.trackId = "674229970930653";' in (
        browser.contents)


def test_webtrekk_parameters_may_include_nextread_url(dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/simple-verlagsnextread')
    view = zeit.web.core.view.Content(context, dummy_request)
    assert view.webtrekk['customParameter']['cp33']
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    view = zeit.web.core.view.Content(context, dummy_request)
    assert 'cp33' not in view.webtrekk['customParameter']


def test_webtrekk_content_id_should_handle_nonascii(
        application, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    dummy_request.traversed = (u'umläut',)
    view = zeit.web.core.view.Content(context, dummy_request)
    assert view.webtrekk_content_id.endswith(u'umläut')


def test_webtrekk_should_include_push_payload_template(
        application, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    push = zeit.push.interfaces.IPushMessages(context)
    push.set(dict(type='mobile'), payload_template='eilmeldung.json')
    view = zeit.web.core.view.Content(context, dummy_request)
    assert view.webtrekk['customParameter']['cp15'] == 'eilmeldung.push'


def test_notification_after_paywall_registration_renders_correctly(
        testserver, selenium_driver):
    message_txt = u'Herzlich willkommen \u2013 viel Spa\xdf beim Lesen!'
    message_txt_error = u'Leider haben Sie kein g\xfcltiges Abonnement ' \
        u'f\xfcr diesen Artikel. Bitte w\xe4hlen Sie unten das ' \
        u'gew\xfcnschte Abo.'
    url_hash = '#success-registration'

    driver = selenium_driver

    def assert_notification(pathname, css_class, text, query=''):
        driver.get('%s%s%s%s' % (testserver.url, pathname, query, url_hash))
        selector = 'link[rel="canonical"][href="{}{}"]'.format(
            testserver.url, pathname)
        try:
            # assure we are seeing the right page
            WebDriverWait(driver, 3).until(
                expected_conditions.presence_of_element_located((
                    By.CSS_SELECTOR, selector)))
            # check for notification element
            WebDriverWait(driver, 1).until(
                expected_conditions.presence_of_element_located((
                    By.CLASS_NAME, css_class)))
        except TimeoutException:
            assert False, 'Timeout notification %s' % driver.current_url
        else:
            notification = driver.find_element_by_class_name(css_class)
            assert text == notification.text
            assert url_hash not in driver.current_url

    # ZON
    assert_notification('/zeit-online/article/01', 'notification--success',
                        message_txt)

    # ZMO
    assert_notification('/zeit-magazin/article/essen-geniessen-spargel-lamm',
                        'notification--success', message_txt)

    # ZCO
    assert_notification('/campus/article/infographic', 'notification--success',
                        message_txt)

    # ZON wrong subscription
    assert_notification('/zeit-online/article/zplus-zeit',
                        'notification--error', message_txt_error,
                        '?C1-Meter-Status=always_paid')


def test_notification_script_does_not_edit_unknown_hashes(
        testserver, selenium_driver):
    driver = selenium_driver
    url_hash = '#debug-clicktracking'
    driver.get('{}/zeit-online/article/01{}'.format(testserver.url, url_hash))
    selector = 'link[rel="canonical"][href="{}{}"]'.format(
        testserver.url, '/zeit-online/article/01')
    try:
        # assure we are seeing the right page
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located((
                By.CSS_SELECTOR, selector)))
    except TimeoutException:
        assert False, 'Timeout notification %s' % driver.current_url
    else:
        assert url_hash in driver.current_url


# mock state ist not resetted in local env
# when running in chain, maybe future versions of
# Chromedriver fix this
@pytest.mark.xfail(reason='Fails locally')
def test_user_name_and_email_are_displayed_correctly(
        testserver, selenium_driver):
    driver = selenium_driver
    # request some arbitrary article page and set loggedin-cookie
    driver.get('%s/zeit-online/article/01' % testserver.url)
    driver.add_cookie({
        'name': 'my_sso_cookie',
        'value': 'just be present',
        'path': '/',
    })
    # check if user email is displayed if no name provided
    with mock.patch('zeit.web.core.security.get_user_info') as get_user:
        get_user.return_value = {
            'ssoid': '123',
            'mail': 'test@example.org',
        }
        driver.get('%s/zeit-online/slenderized-index' % testserver.url)
        assert (u'TEST@EXAMPLE.ORG' in driver.find_element_by_class_name(
            'nav__user-name').text)
    with mock.patch('zeit.web.core.security.get_user_info') as get_user:
        get_user.return_value = {
            'ssoid': '123',
            'mail': 'test@example.org',
            'name': 'jrandom',
        }
        # check if user name is displayed
        driver.get('%s/zeit-online/slenderized-index' % testserver.url)
        assert (u'JRANDOM' in driver.find_element_by_class_name(
            'nav__user-name').text)


def test_notification_after_account_confirmation_renders_correctly(
        testserver, selenium_driver):
    driver = selenium_driver
    url_hash = '#success-confirm-account'
    text = u'Herzlich willkommen! Ihr Konto ist nun aktiviert.'
    # request some arbitrary article page
    driver.get('%s/zeit-online/article/01' % testserver.url)
    driver.add_cookie({
        'name': 'my_sso_cookie',
        'value': 'just be present',
        'path': '/',
    })
    with mock.patch('zeit.web.core.security.get_user_info') as get_user:
        get_user.return_value = {
            'ssoid': '123',
            'mail': 'test@example.org',
            'name': 'jrandom',
        }
        # request the actual dashboard page
        driver.get('%s/konto#success-confirm-account' % testserver.url)
        try:
            # check for notification element
            WebDriverWait(driver, 1).until(
                expected_conditions.presence_of_element_located((
                    By.CLASS_NAME, 'notification--success')))
        except TimeoutException:
            assert False, 'Timeout notification %s' % driver.current_url
        else:
            notification = (driver.find_elements_by_css_selector(
                            '.page__content > *')[1])
            assert text == notification.text
            assert url_hash not in driver.current_url


def test_notification_after_account_change_renders_correctly(
        testserver, selenium_driver):
    driver = selenium_driver
    url_hash = '#success-confirm-change'
    text = u'Ihre Einstellungen wurden gespeichert. Viel Spaß!'
    # request some arbitrary article page
    driver.get('%s/zeit-online/article/01' % testserver.url)
    driver.add_cookie({
        'name': 'my_sso_cookie',
        'value': 'just be present',
        'path': '/',
    })
    with mock.patch('zeit.web.core.security.get_user_info') as get_user:
        get_user.return_value = {
            'ssoid': '123',
            'mail': 'test@example.org',
            'name': 'jrandom',
        }
        # request the actual dashboard page
        driver.get('%s/konto#success-confirm-change' % testserver.url)
        try:
            # check for notification element
            WebDriverWait(driver, 1).until(
                expected_conditions.presence_of_element_located((
                    By.CLASS_NAME, 'notification--success')))
        except TimeoutException:
            assert False, 'Timeout notification %s' % driver.current_url
        else:
            notification = (driver.find_elements_by_css_selector(
                            '.page__content > *')[1])
            assert text == notification.text
            assert url_hash not in driver.current_url


@pytest.mark.xfail(reason='Random loading issues in Selenium.')
def test_notification_renders_correctly_in_wrapper(
        testserver, selenium_driver):
    driver = selenium_driver
    # request some arbitrary article page
    driver.get('%s/zeit-online/article/01' % testserver.url)
    driver.add_cookie({
        'name': 'my_sso_cookie',
        'value': 'just be present',
        'path': '/',
    })
    with mock.patch('zeit.web.core.security.get_user_info') as get_user:
        with mock.patch('zeit.web.core.view.Base.is_wrapped') as is_wrapped:
            is_wrapped.return_value = True
            get_user.return_value = {
                'ssoid': '123',
                'mail': 'test@example.org',
                'name': 'jrandom',
            }
            # request the actual dashboard page
            driver.get('%s/konto#success-confirm-account' % testserver.url)
            try:
                # check for notification element
                WebDriverWait(driver, 1).until(
                    expected_conditions.presence_of_element_located((
                        By.CLASS_NAME, 'notification--success')))
            except TimeoutException:
                assert False, 'Timeout notification %s' % driver.current_url
            else:
                notification = (driver.find_elements_by_css_selector(
                    '.page__content > *')[0])
                assert ('notification--success' in
                        notification.get_attribute('class'))


def test_http_header_should_contain_c1_debug_echoes(testserver):
    response = requests.get(
        '%s/zeit-online/article/simple' % testserver.url,
        headers={
            'C1-Meter-Status': 'always_paid',
            'C1-Meter-User-Status': 'anonymous',
        })
    assert response.headers.get('x-debug-c1-meter-status') == 'always_paid'
    assert response.headers.get('x-debug-c1-meter-user-status') == 'anonymous'


def test_c1_get_param_should_trump_http_header(testserver):
    response = requests.get(
        '{}/zeit-online/article/simple?{}'.format(
            testserver.url,
            'C1-Meter-Status=paywall&C1-Meter-User-Status=anonymous'),
        headers={
            'C1-Meter-Status': 'always_paid',
            'C1-Meter-User-Status': 'anonymous',
        })
    assert 'gate--register' in response.content


def test_js_toggles_are_correctly_returned(application, dummy_request):
    zeit.web.core.application.FEATURE_TOGGLES.unset('update_signals')
    view = zeit.web.core.view.Base(None, None)
    assert ('update_signals', False) in view.js_toggles


def test_js_toggles_are_correctly_displayed(selenium_driver, testserver):
    zeit.web.core.application.FEATURE_TOGGLES.unset('update_signals')
    driver = selenium_driver
    driver.get('%s/zeit-online/index' % testserver.url)
    uds = driver.execute_script('return Zeit.toggles.update_signals')
    assert not uds


def test_article_view_attribute_nooverscrolling_is_not_set(
        application, dummy_request):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    view = zeit.web.site.view_article.Article(article, dummy_request)
    assert not view.no_overscrolling


def test_article_view_attribute_nooverscrolling_is_set(
        application, dummy_request):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/02')
    view = zeit.web.site.view_article.Article(article, dummy_request)
    assert view.no_overscrolling


def test_url_path_not_found_should_render_404(testserver):
    resp = requests.get('%s/zeit-magazin/centerpage/lifestyle'
                        % testserver.url)
    assert u'Dokument nicht gefunden' in resp.text
    assert resp.status_code == 404


def test_not_renderable_content_object_should_render_404(testserver):
    resp = requests.get('%s/zeit-online/quiz/quiz-workaholic' % testserver.url)
    assert resp.status_code == 404


def test_404_page_should_not_render_meta_and_share(testbrowser):

    browser = testbrowser()
    browser.raiseHttpErrors = False
    browser.open('/wurstbrot')

    assert len(browser.cssselect('.byline')) == 0
    assert len(browser.cssselect('.metadata')) == 0
    assert len(browser.cssselect('.sharing-menu')) == 0
    assert len(browser.cssselect('.article-tags')) == 0
    assert len(browser.cssselect('.comment-section')) == 0
    assert len(browser.cssselect(
        '.article-pagination__link[data-ct-label="Startseite"]')) == 1


def test_404_page_should_render_appropriate_links(testserver):
    resp = requests.get('%s/nonexistent' % testserver.url,
                        headers={'Host': 'www.staging.zeit.de'})
    assert 'http://www.staging.zeit.de/index' in resp.text


def test_404_page_should_use_www_for_non_content_hosts(testserver):
    resp = requests.get('%s/nonexistent' % testserver.url,
                        headers={'Host': 'img.staging.zeit.de'})
    assert 'http://www.staging.zeit.de/index' in resp.text
    assert resp.status_code == 404


def test_404_page_should_have_fallback_for_errors(testbrowser):
    folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/error/')
    del folder['404']
    browser = testbrowser()
    browser.raiseHttpErrors = False
    browser.open('/wurstbrot')
    assert 'Status 404: Dokument nicht gefunden.' in browser.contents


def test_retrieve_keywords_from_tms(application):
    zeit.web.core.application.FEATURE_TOGGLES.set('keywords_from_tms')
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['retresco_timeout'] = 0.42

    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    view = zeit.web.core.view.Content(article, None)
    with mock.patch(
            'zeit.retresco.connection.TMS.get_article_keywords') as tms:
        with mock.patch('zeit.content.article.article.Article.keywords',
                        mock.PropertyMock()) as kw:
            tms.return_value = [mock.sentinel.tag]
            assert view.keywords == [mock.sentinel.tag]
            assert not kw.called
            tms.assert_called_with(article, timeout=0.42)


def test_fall_back_on_vivi_keywords_on_tms_failure(application):
    zeit.web.core.application.FEATURE_TOGGLES.set('keywords_from_tms')

    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    view = zeit.web.core.view.Content(article, None)
    with mock.patch(
            'zeit.retresco.connection.TMS.get_article_keywords') as tms:
        with mock.patch('zeit.content.article.article.Article.keywords',
                        mock.PropertyMock()) as kw:
            tms.side_effect = RuntimeError('provoked')
            kw.return_value = [
                zeit.cms.tagging.testing.FakeTag('berlin', 'Berlin')]
            assert len(view.keywords) == 1
            tag = view.keywords[0]
            assert tag.label == 'Berlin'
            assert tag.link is None


def test_icode_cookie_is_set_when_get_parameter_is_detected(
        testserver, selenium_driver):
    driver = selenium_driver
    driver.get(
        '%s/zeit-online/article/simple?wt_cc3=Wurstbrot' % testserver.url)
    cookie = driver.get_cookie('icode')
    assert cookie['value'] == 'Wurstbrot'


@pytest.mark.parametrize(
    'verticals', [
        ('/arbeit/index', 1, 'zarbeit', 'zar'),
        ('/campus/index', 1, 'zcampus', 'zco'),
        ('/zeit-magazin/index', 3, 'zmagazin', 'zmo')
    ])
def test_more_navi_is_present_in_every_vertical_and_has_campaign_param(
        testbrowser, verticals):

    current_page = verticals[0]
    current_number_of_sales_links = verticals[1]
    current_vertical_long = verticals[2]
    current_vertical_short = verticals[3]

    browser = testbrowser(current_page)
    nav_link_sales = browser.cssselect('.nav__sales a')
    assert len(nav_link_sales) == current_number_of_sales_links

    nav_link_abo = nav_link_sales[0]
    nav_link_abo_url = nav_link_abo.attrib['href']
    assert '&utm_source={}&'.format(current_vertical_long) in nav_link_abo_url

    nav_links_more = browser.cssselect('.nav__more-list a')
    for link in nav_links_more:
        link_url = link.attrib['href']
        if '?wt_zmc=' in link_url:
            assert '.{}.'.format(current_vertical_short) in link_url


def test_response_has_surrogate_key_header(testserver):
    response = requests.get(
        '%s/zeit-online/article/simple' % testserver.url)
    assert response.headers.get('surrogate-key') == (
        'http://xml.zeit.de/zeit-online/article/simple')


def test_gdpr_cookie_sets_adcontroller_siteinfo(selenium_driver, testserver):
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules', 'iqd')
    driver = selenium_driver
    driver.get('%s/zeit-online/article/simple' % testserver.url)
    driver.add_cookie({
        'name': 'gdpr',
        'value': 'dnt',
        'path': '/'
    })
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)
    gdpr = driver.execute_script('return adcSiteInfo.gdpr')
    assert gdpr == 'dnt'


def test_view_should_return_channels(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/arbeit/article/01-digitale-nomaden')
    view = zeit.web.arbeit.view_article.Article(
        context, pyramid.testing.DummyRequest())
    assert view.channels == u'entdecken;reisen'


def test_view_should_return_none_if_it_has_no_channels(application):
    author = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/autoren/j_random')
    request = pyramid.testing.DummyRequest()
    view = zeit.web.site.view_author.Author(author, request)
    assert view.channels is None


def test_robots_txt_should_be_dispatched_according_to_host(testserver):
    r = requests.get(
        '%s/robots.txt' % testserver.url,
        headers={'Host': 'www.zeit.de'})
    assert r.status_code == 200
    assert 'Sitemap' in r.content

    r = requests.get(
        '%s/robots.txt' % testserver.url,
        headers={'Host': 'www.staging.zeit.de'})
    assert r.status_code == 200
    assert 'Sitemap' in r.content

    r = requests.get(
        '%s/robots.txt' % testserver.url,
        headers={'Host': 'img.zeit.de'})
    assert r.status_code == 200
    assert 'Sitemap' not in r.content
    assert 'Googlebot-News' in r.content

    r = requests.get(
        '%s/robots.txt' % testserver.url,
        headers={'Host': 'img.staging.zeit.de'})
    assert r.status_code == 200
    assert 'Sitemap' not in r.content
    assert 'Googlebot-News' in r.content

    # Falls back to www if no specific file exists.
    r = requests.get(
        '%s/robots.txt' % testserver.url,
        headers={'Host': 'anything.zeit.de'})
    assert r.status_code == 200
    assert 'Sitemap' in r.content
