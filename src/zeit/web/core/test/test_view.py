# -*- coding: utf-8 -*-
import mock
import pytest
import requests
import urllib2

import pyramid.request
import zope.component

import zeit.web.core.application
import zeit.web.core.date
import zeit.web.core.interfaces
import zeit.web.magazin.view
import zeit.web.magazin.view_article
import zeit.web.magazin.view_centerpage
import zeit.web.site.view_article
import zeit.web.site.view_centerpage

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


@pytest.fixture
def mock_ad_view(application):
    class MockAdView(zeit.web.core.view.Base):

        def __init__(
                self, type, ressort,
                sub_ressort, is_hp=False, banner_id=None, serienname='',
                product_id=None, product_text=None,
                path_info=None, adv_title=''):
            self.type = type
            self.ressort = ressort
            self.sub_ressort = sub_ressort
            self.is_hp = is_hp
            self.product_id = product_id
            self.serie = serienname
            context = mock.Mock()
            context.banner_id = banner_id
            context.advertisement_title = adv_title
            context.product_text = product_text
            context.keywords = []
            request = pyramid.testing.DummyRequest()
            request.path_info = path_info
            self.request = request
            self.context = context

            # fake zeit.web.magazin.view.Base property
            # this starts to get kind of overmocked ... [ms]
            if self.ressort == 'zeit-magazin':
                self.adwords = ['zeitonline', 'zeitmz']

    return MockAdView


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
        application, dummy_request, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'tracking': True, 'iqd': True, 'third_party_modules': True}.get)

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
        testbrowser, dummy_request, monkeypatch):

    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'tracking': True, 'iqd': True, 'third_party_modules': True}.get)

    browser = testbrowser('/zeit-online/article/simple')
    assert 'cre_client.set_origin( window.Zeit.getCeleraOneOrigin() );' in (
        browser.contents)


def test_text_file_content_should_be_rendered(testbrowser):
    browser = testbrowser('/text/dummy')
    assert browser.contents == 'zeit.web\n'


def test_c1_include_script_gets_appended(
        testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'tracking': True, 'third_party_modules': True}.get)
    browser = testbrowser('/zeit-online/article/simple')
    inline = u''.join(browser.xpath('//script/text()'))
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    assert 'script.src = "{}/tracking/tracking.js"'.format(
        conf.get('c1_prefix')) in inline


def test_c1_correct_ressort_on_homepage(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'tracking': True, 'iqd': True, 'third_party_modules': True}.get)
    browser = testbrowser('/zeit-online/slenderized-index')

    assert 'cre_client.set_channel( "homepage" );' in (browser.contents)


def test_c1_client_should_receive_entitlement(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'tracking': True}.get)
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


def test_http_header_should_contain_c1_entitlement(testserver, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'tracking': True}.get)
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


def test_http_header_should_contain_c1_entitlement_id(testserver, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'tracking': True}.get)

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
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    assert isinstance(
        body.values()[-1], zeit.content.article.edit.reference.Gallery)


def test_inline_gallery_should_have_images(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/01')
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    gallery = zeit.web.core.interfaces.IFrontendBlock(body.values()[-1])
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


def test_adcontroller_handles_for_entdecken_und_reisen(mock_ad_view):
    assert mock_ad_view(
        'centerpage', 'entdecken', ''
    ).adcontroller_handle == 'index'
    assert mock_ad_view(
        'centerpage', 'entdecken', 'reisen'
    ).adcontroller_handle == 'centerpage'
    assert mock_ad_view(
        'article', 'entdecken', ''
    ).adcontroller_handle == 'artikel'
    assert mock_ad_view(
        'article', 'entdecken', 'reisen'
    ).adcontroller_handle == 'artikel'


def test_adcontroller_banner_channel_for_entdecken_und_reisen(mock_ad_view):
    assert mock_ad_view(
        'centerpage', 'entdecken', ''
    ).banner_channel == 'reisen/centerpage'
    assert mock_ad_view(
        'centerpage', 'entdecken', 'reisen'
    ).banner_channel == 'reisen/centerpage'


def test_adcontroller_handle_return_value(mock_ad_view):
    assert mock_ad_view(
        'centerpage', 'politik', ''
    ).adcontroller_handle == 'index'
    assert mock_ad_view(
        'centerpage', 'zeit-magazin', ''
    ).adcontroller_handle == 'index'
    assert mock_ad_view(
        'centerpage', 'homepage', '', is_hp=True
    ).adcontroller_handle == 'homepage'
    assert mock_ad_view(
        'centerpage', 'politik', 'deutschland'
    ).adcontroller_handle == 'centerpage'
    assert mock_ad_view(
        'article', 'politik', 'deutschland'
    ).adcontroller_handle == 'artikel'
    assert mock_ad_view(
        'video', 'politik', 'deutschland'
    ).adcontroller_handle == 'video_artikel'
    assert mock_ad_view(
        'quiz', 'politik', 'deutschland'
    ).adcontroller_handle == 'quiz'


def test_banner_channel_mapping_should_apply_first_rule(mock_ad_view):
    assert mock_ad_view(
        'centerpage', 'angebote', '',
        banner_id='mein/ad/code').banner_channel == 'mein/ad/code/centerpage'


def test_banner_channel_mapping_should_apply_second_rule(mock_ad_view):
    assert mock_ad_view(
        'centerpage', 'angebote', '', serienname='meh').banner_channel == (
            'adv/angebote/centerpage')
    assert mock_ad_view(
        'centerpage', 'angebote', '', adv_title='Foo Bar').banner_channel == (
            'adv/foobar/centerpage')
    assert mock_ad_view(
        'centerpage', 'angebote', '',
        banner_id='mcs/xx/yy').banner_channel == ('mcs/xx/yy/centerpage')


def test_banner_channel_mapping_by_path_info(mock_ad_view):
    assert mock_ad_view(
        'centerpage', '', '',
        path_info='/serie/krimizeit-bestenliste').banner_channel == (
            'literatur/krimi-bestenliste/centerpage')


def test_banner_channel_mapping_should_apply_third_rule(mock_ad_view):
    assert mock_ad_view(
        'centerpage', 'zeit-magazin', 'irgendwas'
    ).banner_channel == 'zeitmz/irgendwas/centerpage'
    assert mock_ad_view(
        'centerpage', 'lebensart', ''
    ).banner_channel == 'zeitmz/centerpage'
    assert mock_ad_view(
        'centerpage', 'mobilitaet', ''
    ).banner_channel == 'auto/centerpage'
    assert mock_ad_view(
        'centerpage', 'ranking', ''
    ).banner_channel == 'studium/centerpage'
    assert mock_ad_view(
        'centerpage', 'sport', '', product_id='news'
    ).banner_channel == 'news/centerpage'
    assert mock_ad_view(
        'centerpage', 'politk', '', product_id='sid'
    ).banner_channel == 'sid/centerpage'
    assert mock_ad_view(
        'article', 'foto', ''
    ).banner_channel == 'kultur/article'
    assert mock_ad_view(
        'article', 'wirtschaft', 'geld', serienname='geldspezial'
    ).banner_channel == 'geldspezial/article'
    assert mock_ad_view(
        'centerpage', 'sport', 'zeit wissen'
    ).banner_channel == 'wissen/zeit_wissen/centerpage'
    assert mock_ad_view(
        'centerpage', 'sport', 'zeit campus'
    ).banner_channel == 'wissen/zeit_campus/centerpage'
    assert mock_ad_view(
        'centerpage', 'sport', 'zeit geschichte'
    ).banner_channel == 'wissen/zeit_geschichte/centerpage'
    assert mock_ad_view(
        'centerpage', 'sport', 'das wissen dieser welt'
    ).banner_channel == 'wissen/bildungskanon/centerpage'
    assert mock_ad_view(
        'centerpage', 'wissen', '', serienname="spiele"
    ).banner_channel == 'spiele/centerpage'
    assert mock_ad_view(
        'centerpage', 'campus', 'irgendwas'
    ).banner_channel == 'studium/irgendwas/centerpage'
    assert mock_ad_view(
        'centerpage', 'wissen', '', serienname="reise"
    ).banner_channel == 'reisen/centerpage'
    assert mock_ad_view(
        'centerpage', 'kultur', 'computer'
    ).banner_channel == 'digital/centerpage'
    assert mock_ad_view(
        'centerpage', 'technik', ''
    ).banner_channel == 'digital/centerpage'


def test_banner_channel_mapping_should_apply_fourthandfitfth(mock_ad_view):
    assert mock_ad_view(
        'centerpage', 'politik', '').banner_channel == 'politik/centerpage'
    assert mock_ad_view(
        'centerpage', 'pol', 'deu').banner_channel == 'pol/deu/centerpage'


def test_banner_channel_mapping_should_apply_last_rule(mock_ad_view):
    assert mock_ad_view(
        'centerpage', '', '').banner_channel == 'vermischtes/centerpage'


def test_adcontroller_values_are_correctly_returned(mock_ad_view):
    zw_code = [('$handle', 'centerpage'), ('level2', 'wissen'),
               ('level3', 'zeit_wissen'), ('level4', ''),
               ('$autoSizeFrames', True), ('keywords', 'zeitonline'),
               ('tma', '')]
    zw_test = mock_ad_view(
        'centerpage', 'sport', 'zeit wissen').adcontroller_values
    assert zw_code == zw_test
    zmz_code = [('$handle', 'index'), ('level2', 'zeitmz'),
                ('level3', 'irgendwas'), ('level4', ''),
                ('$autoSizeFrames', True), ('keywords', 'zeitonline,zeitmz'),
                ('tma', '')]
    zmz_test = mock_ad_view(
        'centerpage', 'zeit-magazin', 'irgendwas').adcontroller_values
    assert zmz_code == zmz_test
    zw_code = [('$handle', 'centerpage'), ('level2', 'studium'),
               ('level3', 'unileben'), ('level4', ''),
               ('$autoSizeFrames', True), ('keywords', 'zeitonline'),
               ('tma', '')]
    zw_test = mock_ad_view(
        'centerpage', 'studium', 'uni-leben').adcontroller_values
    assert zw_code == zw_test


def test_adcontroller_values_for_stimmts_series(mock_ad_view):
    adv_test = mock_ad_view(
        'article', 'wissen', '', serienname='Stimmt\'s').adcontroller_values
    adv_code = [('$handle', 'artikel'), ('level2', u'wissen'),
                ('level3', u'serie'), ('level4', 'stimmts'),
                ('$autoSizeFrames', True), ('keywords', 'zeitonline'),
                ('tma', '')]
    assert adv_test == adv_code


def test_banner_advertorial_extrarulez(mock_ad_view):
    adv_test = mock_ad_view(
        'centerpage', 'angebote',
        '', banner_id='angebote/ingdiba',
        adv_title='ingdiba', product_text='Advertorial').adcontroller_values
    adv_code = [('$handle', 'adv_index'), ('level2', u'angebote'),
                ('level3', u'ingdiba'), ('level4', ''),
                ('$autoSizeFrames', True), ('keywords', 'angebote,ingdiba'),
                ('tma', '')]
    assert adv_test == adv_code


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
    view.request.traversed = ('politik', 'index.cp2015')
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


def test_cp2015_suffix_should_lead_to_redirect():
    request = pyramid.testing.DummyRequest()
    request.path = '/foo/baa.cp2015'
    request.url = 'http://foo.xyz.de/foo/baa.cp2015'
    with pytest.raises(
            pyramid.httpexceptions.HTTPMovedPermanently) as redirect:
        zeit.web.core.view.redirect_on_cp2015_suffix(request)

    assert redirect.value.location == 'http://foo.xyz.de/foo/baa'

    request.path = '/foo/baa.cp2015'
    request.url = 'http://foo.xyz.de/foo/baa.cp2015?x=y'

    with pytest.raises(
            pyramid.httpexceptions.HTTPMovedPermanently) as redirect:
        zeit.web.core.view.redirect_on_cp2015_suffix(request)

    assert redirect.value.location == 'http://foo.xyz.de/foo/baa?x=y'

    request.path = '/foo/baa'
    request.url = 'http://foo.xyz.de/foo/baa'
    assert zeit.web.core.view.redirect_on_cp2015_suffix(request) is None


def test_cp2015_redirect_can_be_disabled(application):
    # The context doesn't matter for this test, just needs to be ICMSContent.
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/slenderized-index')
    request = pyramid.testing.DummyRequest(path='/index.cp2015')
    request.registry = application.zeit_app.config.registry
    view = zeit.web.core.view.Base(context, request)
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    settings['redirect_from_cp2015'] = 'False'
    # assert: no HTTPFound is raised.
    view()


def test_content_view_should_provide_lineage_property(
        application, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    content = zeit.web.core.view.Content(context, dummy_request)
    assert len(content.lineage) == 2
    assert all(isinstance(l, dict) for l in content.lineage)


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


def test_iqd_ads_should_utilize_feature_toggles(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'iqd': True, 'third_party_modules': True}.get)
    browser = testbrowser('/zeit-online/article/zeit')
    assert 'AdController.initialize();' in (
        browser.cssselect('head')[0].text_content())

    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'iqd': False, 'third_party_modules': False}.get)
    browser = testbrowser('/zeit-online/article/zeit')
    assert 'AdController.initialize();' not in (
        browser.cssselect('head')[0].text_content())

    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'iqd': True, 'third_party_modules': False}.get)
    browser = testbrowser('/zeit-online/article/zeit')
    assert 'AdController.initialize();' not in (
        browser.cssselect('head')[0].text_content())


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


# XXX align-route-config-uris: Ensure downward compatibility until
# corresponding varnish changes have been deployed.
# Remove this test afterwards!
def test_health_check_should_response_and_have_status_200_XXX(testbrowser):
    browser = testbrowser('/health_check')
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


def test_reader_revenue_status_should_utilize_feature_toggle(
        dummy_request, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'access_status_webtrekk': False}.get)
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert 'cp28' not in view.webtrekk['customParameter'].keys()


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
        selector = 'link[itemprop="mainEntityOfPage"][href="{}{}"]'.format(
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
    selector = 'link[itemprop="mainEntityOfPage"][href="{}{}"]'.format(
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


def test_user_name_and_email_are_displayed_correctly(
        testserver, selenium_driver):
    driver = selenium_driver
    # request some arbitrary article page and set loggedin-cookie
    driver.get('%s/zeit-online/article/01' % testserver.url)
    driver.add_cookie({
        'name': 'my_sso_cookie',
        'value': 'just be present',
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


def test_notification_renders_correctly_in_wrapper(
        testserver, selenium_driver):
    driver = selenium_driver
    # request some arbitrary article page
    driver.get('%s/zeit-online/article/01' % testserver.url)
    driver.add_cookie({
        'name': 'my_sso_cookie',
        'value': 'just be present',
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


def test_js_toggles_are_correctly_returned(
        application, dummy_request, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'update_signals': False}.get)
    view = zeit.web.core.view.Base(None, None)
    assert ('update_signals', False) in view.js_toggles


def test_js_toggles_are_correctly_displayed(
        monkeypatch, selenium_driver, testserver):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'update_signals': False}.get)
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
