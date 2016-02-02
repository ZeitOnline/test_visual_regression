# -*- coding: utf-8 -*-
import json
import mock
import pytest
import requests
import urllib2

import pyramid.request
import zope.component

import zeit.web.core.date
import zeit.web.core.interfaces
import zeit.web.magazin.view
import zeit.web.magazin.view_article
import zeit.web.magazin.view_centerpage
import zeit.web.site.view
import zeit.web.site.view_article
import zeit.web.site.view_centerpage


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
            request = pyramid.testing.DummyRequest()
            request.path_info = path_info
            self.request = request
            self.context = context

    return MockAdView


def test_json_delta_time_from_date_should_return_null(testserver,
                                                      testbrowser):
    browser = testbrowser(
        '{}/json/delta_time?'
        'date=2014-10-14T09%3A06%3A45.950590%2B00%3A00'
        '&base_date=2014-10-15T10%3A06%3A45.950590%2B00%3A00'.format(
            testserver.url))
    assert browser.contents == (
        '{"delta_time": {"time": null}}')


def test_json_delta_time_from_date_should_return_delta_time(testserver,
                                                            testbrowser):
    browser = testbrowser(
        '{}/json/delta_time?'
        'date=2014-10-14T09%3A06%3A45.950590%2B00%3A00'
        '&base_date=2014-10-14T10%3A36%3A45.950590%2B00%3A00'.format(
            testserver.url))
    assert browser.contents == (
        '{"delta_time": {"time": "vor 1 Stunde"}}')


def test_json_delta_time_from_date_should_fallback_to_now_for_base_date(
        testserver, testbrowser):
    browser = testbrowser(
        '{}/json/delta_time?'
        'date=2014-10-15T10%3A06%3A45.950590%2B00%3A00'.format(
            testserver.url))
    assert browser.contents is not None
    assert browser.contents != ''


def test_json_delta_time_from_date_should_return_http_error_on_missing_params(
        testserver, testbrowser):
    with pytest.raises(urllib2.HTTPError):
        testbrowser('{}/json/delta_time'.format(testserver.url))


def test_json_delta_time_from_unique_id_should_return_delta_time(
        testbrowser, clock):
    clock.freeze(zeit.web.core.date.parse_date(
        '2014-10-15T16:23:59.780412+00:00'))

    browser = testbrowser(
        '/json/delta_time?'
        'unique_id=http://xml.zeit.de/zeit-online/main-teaser-setup')
    content = json.loads(browser.contents)
    a1 = 'http://xml.zeit.de/zeit-online/cp-content/article-01'
    a2 = 'http://xml.zeit.de/zeit-online/cp-content/article-02'
    assert content['delta_time'][a1] == 'Vor 1 Stunde'
    assert content['delta_time'][a2] == 'Vor 30 Minuten'


def test_json_delta_time_from_unique_id_should_return_http_error_on_false_uid(
        testserver, testbrowser):
    with pytest.raises(urllib2.HTTPError):
        testbrowser('{}/json/delta_time?unique_id=foo'.format(testserver.url))


def test_json_delta_time_from_unique_id_should_return_http_error_on_article(
        testserver, testbrowser):
    with pytest.raises(urllib2.HTTPError) as error:
        testbrowser('{}/json/delta_time?unique_id='
                    'http://xml.zeit.de/artikel/01'.format(testserver.url))
    assert error.value.getcode() == 400


def test_json_delta_time_from_unique_id_should_use_custom_base_time(
        testserver, testbrowser):
    browser = testbrowser(
        '{}/json/delta_time?base_date=2014-10-15T16%3A06%3A45.95%2B00%3A00&'
        'unique_id=http://xml.zeit.de/zeit-online/main-teaser-setup'.format(
            testserver.url))
    content = json.loads(browser.contents)
    a1 = 'http://xml.zeit.de/zeit-online/cp-content/article-01'
    a2 = 'http://xml.zeit.de/zeit-online/cp-content/article-02'
    assert content['delta_time'][a1] == 'Vor 1 Stunde'
    assert content['delta_time'][a2] == 'Vor 12 Minuten'


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
        'http://xml.zeit.de/artikel/01')
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


def test_c1_content_id_should_correspond_to_traversal_path(
        testbrowser, dummy_request):

    browser = testbrowser('/zeit-online/article/01?page=2')
    assert browser.headers['C1-Track-Content-ID'] == '/zeit-online/article/01'
    assert 'cre_client.set_content_id( "/zeit-online/article/01" );' in (
        browser.contents)


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

    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/04')
    view = zeit.web.core.view.Content(context, dummy_request)
    assert dict(view.c1_header).get('C1-Track-Heading') == (
        u'Kann Leipzig Hypezig berleben')
    assert dict(view.c1_client).get('set_heading') == (
        u'"Kann Leipzig Hypezig überleben?"')
    assert dict(view.c1_header).get('C1-Track-Kicker') == 'Szene-Stadt'
    assert dict(view.c1_client).get('set_kicker') == '"Szene-Stadt"'


def test_c1_service_id_should_be_included_in_tracking_parameters(
        application, dummy_request):

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/simple')
    view = zeit.web.core.view.Content(context, dummy_request)
    assert dict(view.c1_header).get('C1-Track-Service-ID') == 'zon'
    assert dict(view.c1_client).get('set_service_id') == '"zon"'


def test_c1_origin_should_trigger_js_call_for_cre_client(
        testbrowser, dummy_request):

    browser = testbrowser('/zeit-online/article/simple')
    assert 'cre_client.set_origin( window.Zeit.getCeleraOneOrigin() );' in (
        browser.contents)


def test_text_file_content_should_be_rendered(testserver, testbrowser):
    browser = testbrowser('{}/text/dummy'.format(testserver.url))
    assert browser.contents == 'zeit.web\n'


def test_inline_gallery_should_be_contained_in_body(testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    assert isinstance(
        body.values()[-1], zeit.content.article.edit.reference.Gallery)


def test_inline_gallery_should_have_images(testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    gallery = zeit.web.core.interfaces.IFrontendBlock(body.values()[-1])
    assert all(
        zeit.web.core.gallery.IGalleryImage.providedBy(i)
        for i in gallery.itervalues())

    image = gallery.values()[4]
    assert image.src == (
        u'http://xml.zeit.de/galerien/bg-automesse-detroit'
        u'-2014-usa-bilder/chrysler 200 s 1-540x304.jpg')
    assert image.alt is None
    assert image.copyright[0][0] == u'\xa9'


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
        'http://xml.zeit.de/zeit-magazin/index')
    view = zeit.web.magazin.view_centerpage.CenterpageLegacy(
        context, pyramid.testing.DummyRequest())
    assert view.pagetitle == u'My Test SEO - ZEITmagazin ONLINE'


def test_centerpage_should_have_generated_seo_pagetitle(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/lebensart-3')
    view = zeit.web.magazin.view_centerpage.CenterpageLegacy(
        context, pyramid.testing.DummyRequest())
    assert view.pagetitle == u'ZMO CP: ZMO | ZEITmagazin'


def test_article_should_have_postfixed_seo_pagetitle(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/artikel/06')
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
        'http://xml.zeit.de/zeit-magazin/index')
    view = zeit.web.magazin.view_centerpage.CenterpageLegacy(
        context, pyramid.testing.DummyRequest())
    assert view.pagedescription == (u'My Test SEO - ZEITmagazin ONLINE ist '
                                    'die emotionale Seite von ZEIT ONLINE.')


def test_centerpage_should_have_subtitle_seo_pagedesciption(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/lebensart-3')
    view = zeit.web.magazin.view_centerpage.CenterpageLegacy(
        context, pyramid.testing.DummyRequest())
    assert view.pagedescription == u'ZMO CP'


def test_centerpage_should_have_default_seo_pagedescription(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/index')
    view = zeit.web.magazin.view_centerpage.CenterpageLegacy(
        context, pyramid.testing.DummyRequest())
    assert view.pagedescription == zeit.web.magazin.view.Base.seo_title_default


def test_notfound_view_works_for_get(testserver, testbrowser):
    browser = testbrowser()
    with pytest.raises(urllib2.HTTPError) as err:
        browser.open('{}/nonexistent'.format(testserver.url))
    assert err.value.getcode() == 404


def test_notfound_view_works_for_post(testserver, testbrowser):
    browser = testbrowser()
    with pytest.raises(urllib2.HTTPError) as err:
        browser.post('{}/nonexistent'.format(testserver.url), data='')
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


def test_invalid_unicode_should_return_http_400(testbrowser):
    with pytest.raises(urllib2.HTTPError) as info:
        testbrowser('/index%C8')
    assert info.value.getcode() == 400


def test_ivw_uses_hyprid_method_for_apps(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.core:templates/inc/tracking/ivw_ver2.html')
    view = mock.Mock()
    view.is_wrapped = True
    html = tpl.render(view=mock.Mock(), request=mock.Mock())
    assert 'iom.h' in html
    assert 'iom.c' not in html


def test_iqd_ads_should_utilize_feature_toggles(testbrowser, monkeypatch):
    Base = zeit.web.core.view.Base  # NOQA
    monkeypatch.setattr(Base, 'iqd_is_enabled', True)
    monkeypatch.setattr(Base, 'third_party_modules_is_enabled', True)
    browser = testbrowser('/zeit-online/article/zeit')
    assert 'AdController.initialize();' in (
        browser.cssselect('head')[0].text_content())

    monkeypatch.setattr(Base, 'iqd_is_enabled', False)
    monkeypatch.setattr(Base, 'third_party_modules_is_enabled', False)
    browser = testbrowser('/zeit-online/article/zeit')
    assert 'AdController.initialize();' not in (
        browser.cssselect('head')[0].text_content())

    monkeypatch.setattr(Base, 'iqd_is_enabled', True)
    monkeypatch.setattr(Base, 'third_party_modules_is_enabled', False)
    browser = testbrowser('/zeit-online/article/zeit')
    assert 'AdController.initialize();' not in (
        browser.cssselect('head')[0].text_content())


def test_amp_article_should_have_amp_link(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/zeit')
    view = zeit.web.site.view_article.Article(
        context, pyramid.testing.DummyRequest())
    assert view.is_amp
