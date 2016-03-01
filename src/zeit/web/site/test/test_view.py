# coding: utf-8
import mock
import requests

import pyramid.testing

import zeit.web.site.view


def test_login_state_view_should_deliver_correct_destination():
    request = mock.Mock()
    request.registry.settings = {}
    request.session = {}
    request.registry.settings['sso_activate'] = True
    request.registry.settings['community_host'] = "http://community"
    request.registry.settings['sso_url'] = "http://sso"
    request.registry.settings['community_static_host'] = "community_static"
    request.route_url.return_value = 'http://destination_sso/'
    request.params = {}
    result = zeit.web.site.view.login_state(request)
    assert result == {
        'login': 'http://sso/anmelden?url=http://destination_sso',
        'logout': 'http://sso/abmelden?url=http://destination_sso'
    }


def test_article_should_have_breadcrumbs(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    breadcrumbs = browser.cssselect('.footer-breadcrumbs__list')
    assert len(breadcrumbs) == 1


def test_article_should_have_correct_breadcrumb_structure(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    breadcrumbs_items = browser.cssselect('.footer-breadcrumbs__item')
    assert len(breadcrumbs_items) == 3
    breadcrumbs_links = browser.cssselect('.footer-breadcrumbs__link')
    assert len(breadcrumbs_links) == 2


def test_keyword_index_pages_should_fall_back_to_xslt(testserver):
    resp = requests.get(
        '%s/schlagworte/index/A/index' % testserver.url,
        allow_redirects=False)
    assert resp.status_code == 501
    assert resp.headers['x-render-with'] == 'default'


def test_keyword_pages_should_send_redirect(testserver):
    resp = requests.get(
        '%s/schlagworte/orte/Xy/index' % testserver.url,
        allow_redirects=False)
    assert resp.status_code == 301
    assert resp.headers['Location'] == '%s/thema/xy' % testserver.url


def test_commentstart_param_should_trigger_redirect(testserver):
    resp = requests.get(
        '%s/zeit-online/article/zeit?commentstart=2' % testserver.url,
        allow_redirects=False)
    assert resp.status_code == 301
    assert (resp.headers['location'] == (
            '%s/zeit-online/article/zeit' % testserver.url))


def test_page_all_get_param_should_trigger_redirect(testserver):
    resp = requests.get(
        '%s/zeit-online/article/zeit?page=all' % testserver.url,
        allow_redirects=False)
    assert resp.status_code == 301
    assert (resp.headers['location'] == (
            '%s/zeit-online/article/zeit/komplettansicht' % testserver.url))


def test_keyword_redirect_should_handle_nonindex_urls(testserver):
    resp = requests.get(
        '%s/schlagworte/personen/Santa-Klaus' % testserver.url,
        allow_redirects=False)
    assert resp.headers['Location'] == '%s/thema/santa-klaus' % testserver.url

    resp = requests.get(
        '%s/schlagworte/personen/Klaus-Kleber/' % testserver.url,
        allow_redirects=False)
    assert resp.headers['Location'] == '%s/thema/klaus-kleber' % testserver.url


def test_keyword_redirect_should_handle_unicode(testserver):
    resp = requests.get(
        testserver.url + '/schlagworte/orte/istv%C3%A1n-szab%C3%B3/index',
        allow_redirects=False)
    assert resp.status_code == 301
    assert resp.headers['Location'] == (
        u'%s/thema/istván-szabó' % testserver.url).encode('utf-8')


def test_main_nav_should_render_labels(testbrowser):
    browser = testbrowser('/zeit-online/slenderized-index')
    dropdown_label = browser.cssselect('.primary-nav *[data-label]')
    assert len(dropdown_label) == 6  # three elements two times
    assert dropdown_label[0].attrib['data-label'] == 'Anzeige'
    assert dropdown_label[1].attrib['data-label'] == 'Anzeigen'


def test_ressort_literally_returns_correct_ressort(application):
    request = pyramid.testing.DummyRequest()
    # No sub-ressort
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    article_view = zeit.web.site.view_article.Article(context, request)
    assert article_view.ressort_literally == 'Kultur'
    # With sub-ressort
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/quotes')
    article_view = zeit.web.site.view_article.Article(context, request)
    assert article_view.ressort_literally == 'Literatur'
    # Special case: Homepage
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index')
    view = zeit.web.site.view_centerpage.Centerpage(context, request)
    assert view.ressort_literally == 'Homepage'
    # Special case: administratives
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/administratives')
    article_view = zeit.web.site.view_article.Article(context, request)
    assert article_view.ressort_literally == ''


def test_sharing_titles_differ_from_html_title(testbrowser):
    browser = testbrowser('/zeit-online/article/02')

    pagetitle = browser.cssselect('title')[0].text
    og_title = browser.cssselect(
        'meta[property="og:title"]')[0].attrib.get('content')
    twitter_title = browser.cssselect(
        'meta[name="twitter:title"]')[0].attrib.get('content')

    assert og_title + u' | ZEIT ONLINE' == pagetitle
    assert twitter_title + u' | ZEIT ONLINE' == pagetitle


def test_article_should_show_premoderation_warning(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    request = pyramid.testing.DummyRequest()
    request.host_url = 'http://www.zeit.de'
    request.user = {'ssoid': '123', 'blocked': False, 'premoderation': True}
    view = zeit.web.site.view_article.Article(article, request)
    assert view.comment_area['show_premoderation_warning'] is True
