# -*- coding: utf-8 -*-
import datetime
import time

import lxml.objectify
import mock
import pyramid.threadlocal

import zeit.cms.interfaces
import zeit.content.cp.blocks.teaser

import zeit.web.core.template
import zeit.web.site.view_article


def test_filter_strftime_works_as_expected():
    strftime = zeit.web.core.template.strftime
    now = datetime.datetime.now()
    localtime = time.localtime()
    assert strftime('foo', '%s') is None
    assert strftime((2014, 01, 01), '%s') is None
    assert strftime(tuple(now.timetuple()), '%s') == now.strftime('%s')
    assert strftime(now, '%s') == now.strftime('%s')
    assert strftime(localtime, '%s') == time.strftime('%s', localtime)


def test_zon_large_teaser_mapping_is_working_as_expected(application):
    block = mock.Mock()
    block.__iter__ = lambda _: iter(['article'])
    block.layout.id = 'leader'
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-large'
    block.layout.id = 'leader-two-columns'
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-large'
    block.layout.id = 'leader-panorama'
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-large'


def test_teaser_layout_should_be_cached_per_unique_id(application, request):
    request.addfinalizer(pyramid.threadlocal.manager.clear)

    block = mock.Mock()
    block.__iter__ = lambda _: iter(['article'])
    block.layout.id = 'zon-small'
    block.__hash__ = lambda _: 42

    request = pyramid.testing.DummyRequest()
    request._cache_get_layout = {}
    pyramid.threadlocal.manager.push({'request': request})
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-small'
    key = hash((block,))
    assert request._cache_get_layout[key] == 'zon-small'

    request._cache_get_layout = {key: 'zon-large'}
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-large'


def test_get_layout_should_deal_with_all_sort_of_unset_params(
        application, request):
    request.addfinalizer(pyramid.threadlocal.manager.clear)

    block = mock.Mock()
    block.__iter__ = lambda _: iter(['article'])
    block.layout.id = 'zon-small'

    request = pyramid.testing.DummyRequest()
    pyramid.threadlocal.manager.push({'request': request})

    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-small'

    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-small'

    request._cache_get_layout.clear()
    block.uniqueId = None

    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-small'


def test_zon_small_teaser_mapping_is_working_as_expected(application):
    block = mock.Mock()
    block.__iter__ = lambda _: iter(['article'])
    block.layout.id = 'text-teaser'
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-small'
    block.layout.id = 'buttons'
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-small'
    block.layout.id = 'large'
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-small'
    block.layout.id = 'short'
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-small'
    block.layout.id = 'date'
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-small'


def test_zon_fullwidth_teaser_mapping_is_working_as_expected(application):
    block = mock.Mock()
    block.__iter__ = lambda _: iter(['article'])
    block.layout.id = 'leader-fullwidth'
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-fullwidth'


def test_zon_inhouse_teaser_mapping_is_working_as_expected(application):
    block = mock.Mock()
    block.__iter__ = lambda _: iter(['article'])
    block.layout.id = 'parquet-verlag'
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-inhouse'


def test_hide_teaser_mapping_is_working_as_expected(application):
    block = mock.Mock()
    block.__parent__ = mock.Mock()
    block.__parent__.kind = 'major'
    block.__iter__ = lambda _: iter(['article'])
    block.layout.id = 'archive-print-volume'
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'hide'
    block.layout.id = 'archive-print-year'
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'hide'
    block.layout.id = 'two-side-by-side'
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'hide'
    block.layout.id = 'ressort'
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'hide'
    block.layout.id = 'leader-upright'
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'hide'
    block.layout.id = 'buttons-fullwidth'
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'hide'
    block.layout.id = 'parquet-printteaser'
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'hide'


def test_teaser_for_columns_should_have_according_journalistic_format(
        application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/kolumne')
    block = mock.Mock()
    block.__parent__ = mock.Mock()
    block.__parent__.kind = 'major'
    block.layout.id = 'zon-small'
    block.__iter__ = lambda _: iter([article])
    jofo = zeit.web.core.template.get_journalistic_format(block)
    assert jofo == 'column'


def test_teaser_layout_should_only_be_set_for_allowed_areas(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/kolumne')
    block = mock.Mock()
    block.__parent__ = mock.Mock()
    block.__parent__.kind = 'newsticker'
    block.layout.id = 'zon-small'
    block.__iter__ = lambda _: iter([article])
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-small'


def test_teaser_for_series_should_have_according_journalistic_format(
        application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/serie_app_kritik')
    block = mock.Mock()
    block.layout.id = 'zon-small'
    block.__parent__ = mock.Mock()
    block.__parent__.kind = 'major'
    block.__iter__ = lambda _: iter([article])
    jofo = zeit.web.core.template.get_journalistic_format(block)
    assert jofo == 'series'


def test_teaser_for_blogs_should_have_according_journalistic_format(
        application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/blogs/nsu-blog-bouffier')
    block = mock.Mock()
    block.layout.id = 'zon-large'
    block.__parent__ = mock.Mock()
    block.__parent__.kind = 'major'
    block.__iter__ = lambda _: iter([article])
    jofo = zeit.web.core.template.get_journalistic_format(block)
    assert jofo == 'blog'


def test_teaser_layout_for_empty_block_should_be_set_to_hide(application):
    area = mock.Mock()
    area.kind = 'major'
    area.__parent__ = None
    block = zeit.content.cp.blocks.teaser.TeaserBlock(
        area, lxml.objectify.E.block(module='zon-small'))
    block.__iter__ = lambda _: iter([])
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'hide'


def test_teaser_layout_for_series_on_zmo_cps_should_remain_untouched(
        application, monkeypatch):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/04')
    monkeypatch.setattr(zeit.content.cp.interfaces,
                        'ICenterPage', lambda *_: article)
    block = mock.MagicMock()
    block.layout.id = 'zmo-square-large'
    block.__iter__.return_value = iter([article])
    block.__parent__ = mock.Mock()
    block.__parent__.kind = 'major'
    layout = zeit.web.core.template.get_layout(block)
    assert layout == 'zmo-square-large'


def test_breaking_news_should_be_hidden_by_default(testserver, httpbrowser):
    browser = httpbrowser('/zeit-online/index')
    assert len(browser.cssselect('.breaking-news-banner')) == 0


def test_debug_breaking_news_should_force_banner(testserver, httpbrowser):
    browser = httpbrowser('/zeit-online/index?debug=eilmeldung')
    assert len(browser.cssselect('.breaking-news-banner')) == 1


def test_format_webtrekk_returns_safe_text(application):
    text = u'Studium'
    target = 'studium'
    assert zeit.web.core.template.format_webtrekk(text) == target

    text = u'DIE ZEIT Archiv'
    target = 'die_zeit_archiv'
    assert zeit.web.core.template.format_webtrekk(text) == target

    text = u'Ausgabe: 30'
    target = 'ausgabe_30'
    assert zeit.web.core.template.format_webtrekk(text) == target

    text = u'"1992": Bella, ciao'
    target = '1992_bella_ciao'
    assert zeit.web.core.template.format_webtrekk(text) == target

    text = u' Großwildjagd: Der Löwenkopf ist inklusive '
    target = 'grosswildjagd_der_loewenkopf_ist_inklusive'
    assert zeit.web.core.template.format_webtrekk(text) == target

    text = u'Ä Ö Ü á à é è ß !?)&'
    target = 'ae_oe_ue_a_a_e_e_ss'
    assert zeit.web.core.template.format_webtrekk(text) == target


def test_format_iqd_returns_safe_text(application):
    text = u'Studium'
    target = 'studium'
    assert zeit.web.core.template.format_iqd(text) == target

    text = u'DIE ZEIT Archiv'
    target = 'die_zeit_archiv'
    assert zeit.web.core.template.format_iqd(text) == target

    text = u'Ausgabe: 30, für Ü-30 Leser!'
    target = 'ausgabe_30_fuer_ue_30_leser'
    assert zeit.web.core.template.format_iqd(text) == target

    text = u'Ä-Ö-Ü á à é è ß_!?)&'
    target = 'ae_oe_ue_a_a_e_e_ss'
    assert zeit.web.core.template.format_iqd(text) == target


def test_filter_append_get_params_should_create_params():
    request = mock.Mock()
    request.url = 'http://example.com'
    request.GET = {}
    get_params = {'newparam': 'foo'}
    assert 'http://example.com?newparam=foo' == (
        zeit.web.core.template.append_get_params(request, **get_params))


def test_filter_append_get_params_should_append_params():
    request = mock.Mock()
    request.url = 'http://example.com?key1=1'
    get_params = {'newparam': 'foo'}
    assert 'http://example.com?key1=1&newparam=foo' == (
        zeit.web.core.template.append_get_params(request, **get_params))


def test_filter_append_get_params_should_keep_not_overridden_params():
    request = mock.Mock()
    request.url = 'http://example.com?key1=1&key1=2'
    get_params = {'newparam': 'foo'}
    assert 'http://example.com?key1=1&key1=2&newparam=foo' == (
        zeit.web.core.template.append_get_params(request, **get_params))


def test_filter_append_get_params_should_reset_params():
    request = mock.Mock()
    request.url = 'http://example.com?key1=1&key2=2'
    get_params = {u'key1': None}
    assert 'http://example.com?key2=2' == (
        zeit.web.core.template.append_get_params(request, **get_params))


def test_filter_append_get_params_should_accept_unicode():
    request = mock.Mock()
    request.url = 'http://example.com?s%C3%B6ren_mag=k%C3%A4se'
    assert u'http://example.com?s%C3%B6ren_mag=k%C3%A4se' == (
        zeit.web.core.template.append_get_params(request))


def test_pagination_calculation_should_deliver_valid_output():
    pager = zeit.web.core.template.calculate_pagination
    assert pager(1, 1) is None
    assert pager(1, 2) == [1, 2]
    assert pager(6, 7) == [1, 2, 3, 4, 5, 6, 7]

    assert pager(1, 8) == [1, 2, 3, 4, 5, None, 8]
    assert pager(2, 8) == [1, 2, 3, 4, 5, None, 8]
    assert pager(3, 8) == [1, 2, 3, 4, 5, None, 8]
    assert pager(4, 8) == [1, 2, 3, 4, 5, None, 8]

    assert pager(5, 8) == [1, None, 4, 5, 6, 7, 8]
    assert pager(6, 8) == [1, None, 4, 5, 6, 7, 8]
    assert pager(7, 8) == [1, None, 4, 5, 6, 7, 8]
    assert pager(8, 8) == [1, None, 4, 5, 6, 7, 8]

    assert pager(1, 9) == [1, 2, 3, 4, 5, None, 9]
    assert pager(5, 9) == [1, None, 4, 5, 6, None, 9]
    assert pager(6, 9) == [1, None, 5, 6, 7, 8, 9]

    assert pager(20, 400) == [1, None, 19, 20, 21, None, 400]
    assert pager(399, 400) == [1, None, 396, 397, 398, 399, 400]


def test_pagination_calculation_should_fail_gracefully():
    pager = zeit.web.core.template.calculate_pagination
    assert pager('foo', 9) is None
    assert pager('foo', 'bar') is None
    assert pager(None, None) is None
    assert pager(10, 5) is None
    assert pager(2, 1) is None
    assert pager(1, 1) is None


def test_remove_get_params_should_remove_get_params():
    url = "http://example.org/foo/baa?foo=ba&ba=batz&batz=x"
    url = zeit.web.core.template.remove_get_params(url, 'foo', 'batz')

    assert url == "http://example.org/foo/baa?ba=batz"

    url = "http://example.org/foo/baa?foo=ba"
    url = zeit.web.core.template.remove_get_params(url, 'batz')

    assert url == "http://example.org/foo/baa?foo=ba"


def test_join_if_exists_should_should_filter_none():
    assert zeit.web.core.template.join_if_exists(
        ['honey', None, 'flash'], '-') == 'honey-flash'


def test_get_svg_from_file_should_return_svg(application):
    name = 'reload'
    class_name = 'reload-test'
    package = 'zeit.web.site'
    cleanup = True
    a11y = True
    svg = zeit.web.core.template.get_svg_from_file(
        name, class_name, package, cleanup, a11y)
    assert '<svg xmlns="http://www.w3.org/2000/svg"' in svg
    assert 'width="14" height="13" viewBox="0 0 14 13"' in svg
    assert 'class="svg-symbol reload-test"' in svg
    assert 'role="img"' in svg
    assert 'aria-label="Neu laden"' in svg


def test_get_svg_from_file_should_return_no_a11y_svg(application):
    name = 'reload'
    class_name = 'reload-test'
    package = 'zeit.web.site'
    a11y = False
    cleanup = True
    svg = zeit.web.core.template.get_svg_from_file(
        name, class_name, package, cleanup, a11y)
    assert 'aria-hidden="true"' in svg
    assert 'aria-label="Neu laden"' not in svg


def test_get_svg_without_package_should_be_empty_str(application):
    name = 'reload'
    class_name = 'reload-test'
    a11y = False
    cleanup = True
    package = ''
    svg = zeit.web.core.template.get_svg_from_file(
        name, class_name, package, cleanup, a11y)
    assert svg == ''


def test_zplus_is_false_for_free_articles(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/all-blocks')
    assert zeit.web.core.template.zplus_content(content) is False


def test_zplus_is_false_for_non_article_content(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/video/2014-01/1953013471001')
    print zeit.web.core.template.zplus_content(content)
    assert zeit.web.core.template.zplus_content(content) is False


def test_zplus_is_false_for_articles_with_undefined_access(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/zeit')
    assert zeit.web.core.template.zplus_content(content) is False


def test_zplus_abo_is_true_for_abo_articles(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/fischer')
    assert zeit.web.core.template.zplus_abo_content(content) is True


def test_zplus_is_true_for_abo_articles(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/fischer')
    assert zeit.web.core.template.zplus_content(content) is True


def test_zplus_registration_is_false_for_abo_articles(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/fischer')
    assert zeit.web.core.template.zplus_registration_content(content) is False


def test_zplus_abo_is_false_for_registration_articles(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/alter-archivtext')
    assert zeit.web.core.template.zplus_abo_content(content) is False


def test_zplus_register_is_true_for_registration_articles(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/alter-archivtext')
    assert zeit.web.core.template.zplus_registration_content(content) is True


def test_zplus_is_true_for_registration_articles(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/alter-archivtext')
    assert zeit.web.core.template.zplus_content(content) is True


def test_zplus_should_be_toggleable(application, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'reader_revenue': False}.get)
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/fischer')
    assert zeit.web.core.template.zplus_content(content) is False


def test_zplus_abo_should_be_toggleable(application, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'reader_revenue': False}.get)
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/fischer')
    assert zeit.web.core.template.zplus_abo_content(content) is False


def test_zplus_register_icon_should_be_toggleable(application, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'zplus_badge_gray': False}.get)
    path = ('http://xml.zeit.de/zeit-online/cp-content/register/'
            'article-zeit-register')
    content = zeit.cms.interfaces.ICMSContent(path)
    assert not zeit.web.core.template.logo_icon(content)


def test_zplus_badge_should_be_rendered(testbrowser):
    browser = testbrowser('/zeit-online/slenderized-index')
    assert len(browser.cssselect('.teaser-fullwidth__kicker-logo--zplus')) == 1


def test_webtrekk_should_get_logged_off_info_if_user_info_is_empty(
        dummy_request):

    dummy_request.user = {}

    assert zeit.web.core.template.webtrekk_sso_parameter(
        dummy_request) == 'nicht_angemeldet'


def test_webtrekk_should_get_full_login_info_for_logged_in_users(
        dummy_request):

    dummy_request.user = {
        'ssoid': '123',
        'name': 'my_name',
        'email': 'my_email@example.com',
        'entry_url': 'http://xml.zeit.de/entrypoint'}

    assert zeit.web.core.template.webtrekk_sso_parameter(
        dummy_request) == 'angemeldet|http://xml.zeit.de/entrypoint'


def test_webtrekk_should_get_no_login_path_when_entrypoint_is_empty(
        dummy_request):

    dummy_request.user = {
        'ssoid': '123',
        'name': 'my_name',
        'email': 'my_email@example.com',
        'entry_url': ''}

    assert zeit.web.core.template.webtrekk_sso_parameter(
        dummy_request) == 'angemeldet'


def test_adplaces_are_correctly_returned(dummy_request):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/amp')
    view = zeit.web.site.view_article.AcceleratedMobilePageArticle(
        article, dummy_request)
    adplaces = zeit.web.core.template.adplaces(view.pages, [(0, 3), (3, 4)])
    assert adplaces == [(0, 0, 3), (0, 7, 4)]

    short_article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/simple-verlagsnextread')
    view = zeit.web.site.view_article.AcceleratedMobilePageArticle(
        short_article, dummy_request)
    adplaces = zeit.web.core.template.adplaces(view.pages, [(0, 3), (3, 4)])
    assert adplaces == []


def test_remove_tags_from_xml():
    model_block = mock.Mock()
    xml = '<p>Ich esse <em>ein</em> leckeres <a href="#">Wurstbrot</a>.</p>'
    model_block.xml = lxml.etree.fromstring(xml)
    block = zeit.web.core.block.Paragraph(model_block)
    filtered_block = zeit.web.core.template.remove_tags_from_xml(block, 'a')
    assert unicode(
        filtered_block) == 'Ich esse <em>ein</em> leckeres Wurstbrot.\n'
