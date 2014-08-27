# -*- coding: utf-8 -*-
import mock
import lxml.html
import pkg_resources
import pyramid.httpexceptions
import pyramid.response
import pytest
import requests
import urllib2
import zeit.cms.interfaces

import zeit.content.article.edit.reference
import zeit.frontend
import zeit.frontend.gallery
import zeit.frontend.test
import zeit.frontend.view
import zeit.frontend.view_article

from zeit.frontend.test import Browser


def test_base_view_produces_acceptable_return_type():
    class BaseView(zeit.frontend.view.Base):
        """This view class does not implement a __call__ method."""

        pass

    obj = BaseView(mock.Mock(), mock.Mock())
    assert type(type(obj)) is zeit.frontend.view.MetaView, (
        'The type MetaView is used.')
    assert hasattr(obj(), '__iter__'), 'BaseView returns an iterable type.'


def test_response_view_produces_acceptable_return_type():
    class ResponseView(zeit.frontend.view.Base):
        """This view class explicitly returns a pyramid response."""

        def __call__(self):
            return pyramid.response.Response('OK', 200)

    obj = ResponseView(mock.Mock(), mock.Mock())
    assert isinstance(obj(), pyramid.response.Response), (
        'ResponseView retains its return type.')


def test_none_view_produces_acceptable_return_type():
    class NoneView(zeit.frontend.view.Base):
        """This view class implicitly returns None."""

        def __call__(self):
            pass

    obj = NoneView(mock.Mock(), mock.Mock())
    assert hasattr(obj(), '__iter__'), 'NoneView returns an iterable type.'


def test_dict_view_produces_acceptable_return_value():
    class DictView(zeit.frontend.view.Base):
        """This view class returns a dictionary."""

        def __call__(self):
            return {'bar': 1}

    obj = DictView(mock.Mock(), mock.Mock())
    assert obj() == {'bar': 1}, 'DictView retains its return value.'


def test_breadcumb_should_produce_expected_data():
    context = mock.Mock()
    context.ressort = 'zeit-magazin'
    context.sub_ressort = 'mode-design'
    context.title = 'This is my title'

    zeit.frontend.view_article._navigation = {
        'start': (
            'Start',
            'http://www.zeit.de/index',
            'myid1'
        ),
        'zmo': (
            'ZEIT Magazin',
            'http://www.zeit.de/zeit-magazin/index',
            'myid_zmo'
        ),
        'leben': (
            'Leben',
            'http://www.zeit.de/zeit-magazin/leben/index',
            'myid2'
        ),
        'mode-design': (
            'Mode & Design',
            'http://www.zeit.de/zeit-magazin/mode-design/index',
            'myid3'
        ),
        'essen-trinken': (
            'Essen & Trinken',
            'http://www.zeit.de/zeit-magazin/essen-trinken/index',
            'myid4'
        )
    }

    article = zeit.frontend.view_article.Article(context, mock.Mock())

    l = [
        ('Start', 'http://www.zeit.de/index', 'myid1'),
        ('ZEIT Magazin', 'http://www.zeit.de/zeit-magazin/index', 'myid_zmo'),
        ('Mode & Design', 'http://www.zeit.de/zeit-magazin/mode-design/index',
            'myid3'),
        ('This is my title', ''), ]

    assert article.breadcrumb == l


def test_breadcrumb_should_be_shorter_if_ressort_or_sub_ressort_is_unknown():
    context = mock.Mock()
    context.ressort = 'zeit-magazin'
    context.sub_ressort = 'lebensartx'
    context.title = 'This is my title'

    zeit.frontend.view_article._navigation = {
        'start': (
            'Start',
            'http://www.zeit.de/index',
            'myid1'
        ),
        'zmo': (
            'ZEIT Magazin',
            'http://www.zeit.de/zeit-magazin/index',
            'myid_zmo'
        ),
        'leben': (
            'Leben',
            'http://www.zeit.de/zeit-magazin/leben/index',
            'myid2'
        ),
        'mode-design': (
            'Mode & Design',
            'http://www.zeit.de/zeit-magazin/mode-design/index',
            'myid3'
        ),
        'essen-trinken': (
            'Essen & Trinken',
            'http://www.zeit.de/zeit-magazin/essen-trinken/index',
            'myid4'
        )
    }

    article = zeit.frontend.view_article.Article(context, mock.Mock())

    l = [
        ('Start', 'http://www.zeit.de/index', 'myid1'),
        ('ZEIT Magazin', 'http://www.zeit.de/zeit-magazin/index', 'myid_zmo'),
        ('This is my title', ''), ]

    assert article.breadcrumb == l


def test_linkreach_property_should_be_set(application, app_settings):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    request = mock.Mock()
    request.registry.settings.linkreach_host = app_settings['linkreach_host']
    article_view = zeit.frontend.view_article.Article(context, request)
    article_view.request.url = 'artikel/03'
    article_view.request.traversed = ('foo',)
    article_view.request.route_url = lambda *args: ''
    assert isinstance(article_view.linkreach, dict)


def test_linkreach_property_should_fetch_correct_data(testserver,
                                                      app_settings):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    request = mock.Mock()
    request.registry.settings.linkreach_host = app_settings['linkreach_host']
    article_view = zeit.frontend.view_article.Article(context, request)
    article_view.request.url = 'foo'
    article_view.request.traversed = ('foo',)
    article_view.request.route_url = lambda *args: ''
    assert article_view.linkreach['total'] == ('1,1', 'Tsd.')


def test_header_img_should_be_first_image_of_content_blocks(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    url = 'http://xml.zeit.de/exampleimages/artikel/05/01.jpg'
    assert article_view.header_img.src == url


def test_article_should_have_author_box(testserver):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/artikel/autorenbox')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    body = zeit.content.article.edit.interfaces.IEditableBody(
        article_view.context)
    assert type(body.values()[2]) == (
        zeit.content.article.edit.reference.Portraitbox)


def test_header_img_should_be_none_if_we_have_a_wrong_layout(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.header_img is None


def test_header_video_should_be_first_video_of_content_blocks(application):
    vid_url = 'http://xml.zeit.de/artikel/header_video'
    context = zeit.cms.interfaces.ICMSContent(vid_url)
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    url = ('http://brightcove.vo.llnwd.net/pd15/media/18140073001/201401/'
           '3809/18140073001_3094832002001_Aurora-Borealis--Northern-Lights'
           '--Time-lapses-in-Norway-Polarlichter-Der-Himmel-brennt.mp4')
    assert article_view.header_video.highest_rendition == url


def test_header_video_should_be_none_if_we_have_a_wrong_layout(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.header_video is None


def test_header_elem_should_be_img_if_there_is_a_header_img(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert type(article_view.header_elem) == (
        zeit.frontend.block.HeaderImageStandard)


def test_header_elem_should_be_video_if_there_is_a_header_video(application):
    xml = 'http://xml.zeit.de/artikel/header_video'
    context = zeit.cms.interfaces.ICMSContent(xml)
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert type(article_view.header_elem) == zeit.frontend.block.HeaderVideo


def test_header_image_should_be_none_if_adapted_as_regular_image(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    assert zeit.frontend.block.Image(body.values()[0]) is None


def test_image_view_returns_image_data_for_filesystem_connector(testserver):
    r = requests.get(testserver.url +
        '/exampleimages/artikel/01/schoppenstube/schoppenstube-540x304.jpg')
    assert r.headers['content-type'] == 'image/jpeg'
    assert r.text.startswith(u'\ufffd\ufffd\ufffd\ufffd\x00')


def test_footer_should_have_expected_markup(testserver):
    browser = Browser('%s/artikel/01' % testserver.url)
    elem = browser.cssselect('footer.main-footer')[0]
    # assert normal markup
    expect = '<footer class="main-footer">'\
        '<div class="main-footer__box is-constrained is-centered">'\
        '<div class="main-footer__logo icon-logo-zmo-small"></div>'\
        '<div class="main-footer__links"><div><ul><li>VERLAG</li>'\
        '<li><a href="http://www.zeit-verlagsgruppe.de/anzeigen/">'\
        'Mediadaten</a></li><li><a href="'\
        'http://www.zeitverlag.de/presse/rechte-und-lizenzen">'\
        'Rechte &amp; Lizenzen</a></li>'\
        '</ul></div><div><ul><li><a class="js-toggle-copyrights">'\
        'Bildrechte</a></li>'\
        '<li><a href="http://www.zeit.de/hilfe/datenschutz">'\
        'Datenschutz</a></li>'\
        '<li><a href="'\
        'http://www.iqm.de/Medien/Online/nutzungsbasierte_'\
        'onlinewerbung.html">Cookies</a></li>'\
        '<li><a href="http://www.zeit.de/administratives/'\
        'agb-kommentare-artikel">AGB</a></li>'\
        '<li><a href="http://www.zeit.de/impressum/index">Impressum</a></li>'\
        '<li><a href="http://www.zeit.de/hilfe/hilfe">Hilfe/ Kontakt</a></li>'\
        '</ul></div></div></div></footer>'
    got = [s.strip() for s in lxml.html.tostring(elem).splitlines()]
    got = "".join(got)
    assert expect == got


def test_inline_gallery_should_be_contained_in_body(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    assert (
        type(body.values()[14]) == zeit.content.article.edit.reference.Gallery)


def test_inline_gallery_should_have_images(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    gallery = zeit.frontend.block.IFrontendBlock(body.values()[14])
    assert all(
        zeit.frontend.gallery.IGalleryImage.providedBy(i)
        for i in gallery.itervalues())

    image = gallery.values()[4]
    assert image.src == (
        u'http://xml.zeit.de/galerien/bg-automesse-detroit'
        '-2014-usa-bilder/chrysler 200 s 1-540x304.jpg')
    assert image.alt is None
    assert image.copyright[0][0] == u'\xa9'


def test_article_request_should_have_body_element(testserver):
    browser = zeit.frontend.test.Browser('%s/artikel/05' % testserver.url)
    assert (
        '<body itemscope itemtype="http://schema.org/WebPage">'
        ) in browser.contents
    assert '</body>' in browser.contents


def test_article_request_should_have_html5_doctype(testserver):
    browser = zeit.frontend.test.Browser('%s/artikel/05' % testserver.url)
    assert '<!DOCTYPE html>' in browser.contents


def test_artikel05_should_have_header_image(testserver):
    browser = zeit.frontend.test.Browser('%s/artikel/05' % testserver.url)
    assert '<div class="article__head-wrap">' in browser.contents
    assert '<div class="scaled-image is-pixelperfect">' in browser.contents
    assert 'class="article__main-image--longform' in browser.contents


def test_column_should_have_header_image(testserver):
    browser = zeit.frontend.test.Browser(
        '%s/artikel/standardkolumne-beispiel' % testserver.url)
    assert '<div class="article__column__headerimage">' in browser.contents
    assert '<div class="scaled-image">' in browser.contents
    assert ('<img alt="Die ist der image sub text\n" title="Die ist der image'
            ' sub text\n" class=" figure__media"') in browser.contents


def test_column_should_not_have_header_image(testserver):
    browser = zeit.frontend.test.Browser(
        '%s/artikel/standardkolumne-ohne-bild-beispiel' % testserver.url)
    assert '<div class="article__column__headerimage">' not in browser.contents


def test_health_check_should_response_and_have_status_200(testserver):
    browser = zeit.frontend.test.Browser('%s/health_check' % testserver.url)
    assert browser.headers['Content-Length'] == '2'
    resp = zeit.frontend.view.health_check('request')
    assert resp.status_code == 200


def test_a_404_request_should_be_from_zon_main_page(testserver):
    browser = zeit.frontend.test.Browser()
    browser.handleErrors = False
    with pytest.raises(urllib2.HTTPError):
        browser.open('%s/this_is_a_404_page_my_dear' % testserver.url)
        assert '404 Not Found' in str(browser.headers)

    assert 'Dokument nicht gefunden' in browser.contents


def test_content_should_have_type(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    content_type = type(context).__name__.lower()
    assert content_type is not None


def test_tracking_type_is_provided(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.tracking_type == 'Artikel'


def test_artikel02_has_lebensart_ressort(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.ressort == 'lebensart'


def test_artikel02_has_leben_sub_ressort(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.sub_ressort == 'leben'


def test_artikel02_has_correct_banner_channel(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.banner_channel == 'zeitmz/leben/article'


def test_artikel05_has_rankedTagsList(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.rankedTagsList is not None
    assert article_view.rankedTagsList != ''


def test_artikel01_has_correct_authorsList(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.authorsList == 'Anne Mustermann'


def test_artikel08_has_correct_authorsList(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/08')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.authorsList == 'Anne Mustermann;Oliver Fritsch'


def test_artikel05_has_set_text_length(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.text_length is not None


def test_article05_has_correct_dates(testserver):
    # updated article
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.date_last_published_semantic.isoformat() == (
        '2013-11-03T08:10:00.626737+01:00')
    assert article_view.date_first_released.isoformat() == (
        '2013-10-24T08:00:00+02:00')
    assert article_view.show_article_date.isoformat() == (
        '2013-11-03T08:10:00.626737+01:00')


def test_article03_has_correct_dates(testserver):
    # not updated article
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.date_first_released.isoformat() == (
        '2013-07-30T17:20:50.176115+02:00')
    assert article_view.show_article_date.isoformat() == (
        '2013-07-30T17:20:50.176115+02:00')


def test_article09_has_correct_date_formats(testserver):
    # print article, updated
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/09')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.show_date_format == 'long'
    assert article_view.show_date_format_seo == 'short'


def test_article10_has_correct_date_formats(testserver):
    # online article, updated
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/10')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.show_date_format == 'long'
    assert article_view.show_date_format_seo == 'long'


def test_article08_has_first_author(testserver):
    xml = 'http://xml.zeit.de/artikel/08'
    context = zeit.cms.interfaces.ICMSContent(xml)
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.authors[0]['name'] == u'Anne Mustermann'
    assert article_view.authors[0]['suffix'] == ' und'
    assert article_view.authors[0]['prefix'] == ' von'
    assert article_view.authors[0]['location'] == ', Berlin'


def test_article08_has_second_author(testserver):
    xml = 'http://xml.zeit.de/artikel/08'
    context = zeit.cms.interfaces.ICMSContent(xml)
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.authors[1]['name'] == u'Oliver Fritsch'
    assert article_view.authors[1]['suffix'] == ''
    assert article_view.authors[1]['prefix'] == ''
    assert article_view.authors[1]['location'] == ', London'


def test_article08_has_correct_genre(testserver):
    # 'ein'
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/08')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.genre == 'ein Kommentar'


def test_article09_has_correct_genre(testserver):
    # 'eine'
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/09')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.genre == 'eine Glosse'


def test_article05_has_no_genre(testserver):
    # no genre
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.genre is None


def test_article08_has_correct_source(testserver):
    # print source
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/08')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.source == 'DIE ZEIT Nr. 26/2008'


def test_article10_has_correct_source(testserver):
    # online source
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/10')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.source == 'golem.de'


def test_article03_has_empty_source(testserver):
    # zon source
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.source is None


def test_article_has_correct_twitter_card_type(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.twitter_card_type == 'summary_large_image'


def test_longform_has_correct_twitter_card_type(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.twitter_card_type == 'summary_large_image'


def test_article_has_correct_image_group(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert article_view.image_group.uniqueId == \
        'http://xml.zeit.de/exampleimages/artikel/01/schoppenstube'


def test_article_has_correct_sharing_image(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert zeit.frontend.template.closest_substitute_image(
        article_view.image_group, 'og-image').uniqueId == \
        'http://xml.zeit.de/exampleimages/artikel/01/schoppenstube/schoppenstube-540x304.jpg'
    assert zeit.frontend.template.closest_substitute_image(
        article_view.image_group, 'twitter-image-large').uniqueId == \
        'http://xml.zeit.de/exampleimages/artikel/01/schoppenstube/schoppenstube-540x304.jpg'


def test_ArticlePage_should_throw_404_if_page_is_nan(testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    page = zeit.frontend.view_article.ArticlePage(article, mock.Mock())
    page.request.registry.settings = {}
    page.request.path_info = 'article/03/seite-x'
    with pytest.raises(pyramid.httpexceptions.HTTPNotFound):
        page()


def test_ArticlePage_should_throw_404_if_no_page_in_path(testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    page = zeit.frontend.view_article.ArticlePage(article, mock.Mock())
    page.request.registry.settings = {}
    page.request.path_info = 'article/03/seite-'
    with pytest.raises(pyramid.httpexceptions.HTTPNotFound):
        page()


def test_ArticlePage_should_throw_404_if_no_pages_are_exceeded(testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    page = zeit.frontend.view_article.ArticlePage(article, mock.Mock())
    page.request.registry.settings = {}
    page.request.path_info = u'article/03/seite-9'
    with pytest.raises(pyramid.httpexceptions.HTTPNotFound):
        page()


def test_ArticlePage_should_not_work_if_view_name_is_seite_1(testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    page = zeit.frontend.view_article.ArticlePage(article, mock.Mock())
    page.request.registry.settings = {}
    page.request.path_info = u'article/03/seite-1'
    with pytest.raises(pyramid.httpexceptions.HTTPNotFound):
        page()


def test_ArticlePage_should_work_if_pages_from_request_fit(testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    page = zeit.frontend.view_article.ArticlePage(article, mock.Mock())
    page.request.registry.settings = {}
    page.request.path_info = 'article/03/seite-3'
    page()
    assert len(page.pages) == 7


def test_ArticlePage_komplett_should_show_all_pages(testserver):
    browser = zeit.frontend.test.Browser(
        '%s/artikel/03/komplettansicht' % testserver.url)
    assert 'Chianti ein Comeback wirklich verdient' in browser.contents


def test_pagination_dict_should_have_correct_entries(testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')

    view = zeit.frontend.view_article.ArticlePage(article, mock.Mock())
    view.request.path_info = u'article/03/seite-2'
    view.request.traversed = (u'artikel', u'03')
    view.request.route_url.return_value = '/'

    assert view.pagination['current'] == 2
    assert view.pagination['total'] == 7
    assert view.pagination['next_page_title'] == (
        u'Sogar die eckige Flasche kommt zur\xfcck')

    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    view = zeit.frontend.view_article.Article(article, mock.Mock())
    view.request.traversed = ('artikel', '03')
    view.request.route_url.return_value = '/'

    assert view.pagination['current'] == 1
    assert view.pagination['total'] == 7
    assert view.pagination['next_page_title'] == (
        u'Sogar die runde Flasche kommt zur\xfcck')


def test_pagination_next_title_should_be_in_html(testserver):
    browser = zeit.frontend.test.Browser(
        '%s/artikel/03/seite-2' % testserver.url)
    assert 'Auf Seite 3' in browser.contents
    assert 'Sogar die eckige Flasche kommt' in browser.contents


def test_pagination_urls_list_should_have_correct_entries_paged_article(
        testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')

    view = zeit.frontend.view_article.ArticlePage(article, mock.Mock())
    view.request.path_info = u'article/03/seite-2'
    view.request.traversed = ('artikel', '03')
    view.request.route_url.return_value = '/'

    assert view.pages_urls[0] == '/artikel/03'
    assert view.pages_urls[1] == '/artikel/03/seite-2'
    assert view.pages_urls[2] == '/artikel/03/seite-3'


def test_pagination_urls_list_should_have_correct_entries_single_article(
        testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')

    view = zeit.frontend.view_article.ArticlePage(article, mock.Mock())
    view.request.path_info = u'article/01'
    view.request.traversed = (u'artikel', u'01')
    view.request.route_url.return_value = '/'

    assert view.pages_urls[0] == '/artikel/01'
    assert len(view.pages_urls) == 1


def test_pagination_next_page_url_is_working(testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    view = zeit.frontend.view_article.Article(article, mock.Mock())
    view.request.traversed = (u'artikel', u'03')
    view.request.route_url.return_value = '/'

    assert view.pagination['next_page_url'] == '/artikel/03/seite-2'


def test_pagination_next_page_url_on_last_page_is_none(testserver):
    browser = zeit.frontend.test.Browser(
        '%s/artikel/03/seite-7' % testserver.url)
    content = '<span class="icon-pagination-next">Vor</span>'

    assert content in browser.contents


def test_pagination_prev_page_url_is_working(testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')

    view = zeit.frontend.view_article.ArticlePage(article, mock.Mock())
    view.request.path_info = u'article/03/seite-2'
    view.request.traversed = (u'artikel', u'03')
    view.request.route_url.return_value = '/'

    assert view.pagination['prev_page_url'] == u'/artikel/03'


def test_pagination_prev_page_url_on_first_page_is_none(testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    view = zeit.frontend.view_article.Article(article, mock.Mock())
    view.request.traversed = ('artikel', '03')
    view.request.route_url.return_value = '/'
    assert view.pagination['prev_page_url'] is None


def test_article09_should_have_a_nextread(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/09')
    view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert view.nextread is not None


def test_article01_should_not_have_a_nextread(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert view.nextread is None


def test_cp_teaser_with_comments_should_get_comments_count(testserver):
    request = mock.Mock()
    request.registry.settings.node_comment_statistics = (
        'data/node-comment-statistics.xml')
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo')
    view = zeit.frontend.view_centerpage.Centerpage(cp, request)
    view()  # trigger __call__ method
    comment_count = view.teaser_get_commentcount(
        'http://xml.zeit.de/centerpage/article_image_asset')
    assert comment_count == '22'
    # For teaser uniquId with no entry in node-comment-statistics
    # teaser_get_commentcount should return None
    comment_count = view.teaser_get_commentcount(
        'http://xml.zeit.de/centerpage/article_image_assetXXX')
    assert comment_count is None


def test_caching_headers_should_be_set(testserver):
    browser = zeit.frontend.test.Browser('%s/artikel/05' % testserver.url)
    assert browser.headers['cache-control'] == 'max-age=300'


def test_article_should_have_correct_js_view(testserver):
    bc = zeit.frontend.test.Browser('%s/artikel/01' % testserver.url).contents
    assert "window.ZMO.view = {" in bc
    assert "'banner_channel': 'zeitmz/modeunddesign/article'," in bc
    assert "'ressort': 'zeit-magazin'," in bc
    assert "'sub_ressort': 'mode-design'," in bc
    assert "'type': 'article'," in bc


def test_centerpage_should_have_correct_js_view(testserver):
    bc = zeit.frontend.test.Browser(
        '%s/centerpage/lebensart' % testserver.url).contents
    assert "window.ZMO.view = {" in bc
    assert "'banner_channel': 'zeitmz/leben/centerpage'," in bc
    assert "'ressort': 'lebensart'," in bc
    assert "'sub_ressort': 'leben'," in bc
    assert "'type': 'centerpage'," in bc


def test_gallery_should_have_correct_js_view(testserver):
    b = zeit.frontend.test.Browser(
        '%s/galerien/fs-desktop-schreibtisch-computer' % testserver.url)
    bc = b.contents
    assert "window.ZMO.view = {" in bc
    assert "'banner_channel': 'zeitmz/leben/article'," in bc
    assert "'sub_ressort': 'leben'," in bc
    assert "'ressort': 'zeit-magazin'," in bc
    assert "'type': 'gallery'," in bc


def test_iqd_mobile_settings_are_filled(testserver):
    # tested just as examlpe for an article here, all possible combinations
    # are tested in test_banner.py integration tests
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    view = zeit.frontend.view_article.Article(
        article, mock.MagicMock(return_value=''))
    assert view.iqd_mobile_settings.get('top') == '445612'
    assert view.iqd_mobile_settings.get('middle') == '445612'
    assert view.iqd_mobile_settings.get('bottom') == '445612'


def test_http_header_should_contain_zmo_version(testserver):
    pkg = pkg_resources.get_distribution('zeit.frontend')
    pkg_version = pkg.version
    head_version = requests.head(
        testserver.url + "/zeit-magazin/index").headers['x-zmoversion']
    assert pkg_version == head_version

def test_feature_longform_template_should_have_zon_logo_header(jinja2_env):
    tpl = jinja2_env.get_template('templates/feature_longform.html')

    # jinja2 has a blocks attribute which generates a stream,
    # if called with context. We can use it with a html parser.
    html_str = " ".join(list(tpl.blocks['longform_logo']({})))
    html = lxml.html.fromstring(html_str)
    elem = html.cssselect('.main-nav__logo__img.icon-logo-zon-large')[0]
    assert elem.text == 'ZEIT ONLINE'
    assert elem.get('title') == 'ZEIT ONLINE'

    elem =  html.cssselect('.main-nav__logo')[0]
    assert elem.get('href') == 'http://www.zeit.de/index'

def test_feature_longform_template_should_have_zon_logo_footer(jinja2_env):
    tpl = jinja2_env.get_template('templates/feature_longform.html')
    html_str = " ".join(list(tpl.blocks['footer_logo']({})))
    html = lxml.html.fromstring(html_str)
    assert len(html.cssselect('.main-footer__logo.icon-logo-zon-small')) == 1


