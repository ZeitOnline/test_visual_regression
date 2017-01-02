# coding: utf-8
import urllib2

import jwt
import pyramid.testing
import requests
import zope.component

import zeit.web.core.interfaces
import zeit.web.site.view


def test_login_state_view_should_deliver_correct_destination(dummy_request):
    dummy_request.route_url = lambda *args, **kw: 'http://destination_sso/'
    r = zeit.web.site.view.login_state(dummy_request)
    assert (r['login'] ==
            'http://sso.example.org/anmelden?url=http://destination_sso')
    assert (r['logout'] ==
            'http://sso.example.org/abmelden?url=http://destination_sso')


def test_article_should_have_breadcrumbs(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    breadcrumbs = browser.cssselect('.breadcrumbs__list')
    assert len(breadcrumbs) == 1


def test_article_should_have_correct_breadcrumb_structure(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    breadcrumbs_items = browser.cssselect('.breadcrumbs__item')
    assert len(breadcrumbs_items) == 3
    breadcrumbs_links = browser.cssselect('.breadcrumbs__link')
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


def test_keyword_redirect_should_handle_pagination(testserver):
    resp = requests.get(
        testserver.url + '/schlagworte/orte/rom/seite-3',
        allow_redirects=False)
    assert resp.status_code == 301
    assert resp.headers['Location'] == '%s/thema/rom?p=3' % testserver.url


def test_keyword_redirect_should_reject_invalid_urls(testserver):
    resp = requests.get(
        testserver.url + '/schlagworte/personen/%0DSanta-Klaus/index',
        allow_redirects=False)
    assert resp.status_code == 400


def test_main_nav_should_render_labels(testbrowser):
    browser = testbrowser('/zeit-online/slenderized-index')
    dropdown_label = browser.cssselect('.nav__ressorts-list *[data-label]')
    assert len(dropdown_label) == 3
    assert dropdown_label[0].attrib['data-label'] == 'Anzeige'
    assert dropdown_label[1].attrib['data-label'] == 'Anzeigen'


def test_ressort_literally_returns_correct_ressort(application):
    request = pyramid.testing.DummyRequest()
    # No sub-ressort
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    article_view = zeit.web.site.view_article.Article(context, request)
    assert article_view.ressort_literally == u'Film & TV'
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


def test_schema_org_publisher_mark_up(testbrowser):
    # @see https://developers.google.com/structured-data/rich-snippets/articles
    # #article_markup_properties
    browser = testbrowser('/zeit-online/article/01')
    publisher = browser.cssselect('[itemprop="publisher"]')[0]
    logo = publisher.cssselect('[itemprop="logo"]')[0]

    # check Organization
    assert publisher.get('itemtype') == 'http://schema.org/Organization'
    assert publisher.cssselect('[itemprop="name"]')[0].get('content') == (
        'ZEIT ONLINE')
    assert publisher.cssselect('[itemprop="url"]')[0].get('href') == (
        'http://localhost/index')
    assert logo.get('itemtype') == 'http://schema.org/ImageObject'
    assert logo.cssselect('[itemprop="url"]')[0].get('content') == (
        'http://localhost/static/latest/images/'
        'structured-data-publisher-logo-zon.png')
    assert logo.cssselect('[itemprop="width"]')[0].get('content') == '565'
    assert logo.cssselect('[itemprop="height"]')[0].get('content') == '60'


def test_user_dashboard_has_correct_elements(testbrowser, sso_keypair):
    # browser without sso session
    b = testbrowser()
    b.mech_browser.set_handle_redirect(False)
    try:
        b.open('/konto')
    except urllib2.HTTPError, e:
        assert e.getcode() == 302
        assert (e.hdrs.get('location') ==
                'http://sso.example.org?url=http%3A%2F%2Flocalhost%2Fkonto')

    # browser with sso session
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['sso_key'] = sso_keypair['public']
    sso_cookie = jwt.encode(
        {'id': 'ssoid'}, sso_keypair['private'], 'RS256')
    testbrowser.cookies.forURL(
        'http://localhost')['my_sso_cookie'] = sso_cookie
    testbrowser.open('/login-state')
    browser = testbrowser('/konto')

    # main structure
    assert len(browser.cssselect('.dashboard')) == 1
    assert len(browser.cssselect('.dashboard__upper')) == 1
    assert len(browser.cssselect('.dashboard__lower')) == 1
    assert len(browser.cssselect('.dashboard__content')) == 1
    assert len(browser.cssselect('.dashboard__header')) == 1
    assert len(browser.cssselect('.article-pagination')) == 1

    # head
    assert (browser.cssselect('.dashboard__kicker')[0].text.strip() ==
            'Herzlich Willkommen')
    assert (browser.cssselect('.dashboard__title')[0].text.strip() ==
            'Mein Konto')
    assert len(browser.cssselect('.dashboard__user')) == 1
    assert (browser.cssselect('.dashboard__user-name')[0].text.strip() ==
            'test-user')
    assert len(browser.cssselect('.dashboard__user-image')) == 1
    assert len(browser.cssselect('.dashboard__box--is-header')) == 1

    # body
    assert len(browser.cssselect('.dashboard__box')) == 6
    assert len(browser.cssselect('.dashboard__box-title')) == 6
    assert (browser.cssselect('.dashboard__box-title')[1].text.strip() ==
            'Meine Abonnements')
    assert (browser.cssselect('.dashboard__box-title')[3].text.strip() ==
            'Spiele')
    assert (browser.cssselect('.dashboard__box-list')[2]
            .cssselect('a')[0].text.strip() == u'ZEIT Audio hören')
