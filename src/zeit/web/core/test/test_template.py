# -*- coding: utf-8 -*-
import datetime
import itertools
import os
import sys
import time

import gocept.httpserverlayer.static
import jinja2
import lxml.html
import lxml.objectify
import mock
import pytest
import venusian
import webob.multidict
import zope.component

import zeit.cms.interfaces
import zeit.content.cp.blocks.teaser

import zeit.web.core.decorator
import zeit.web.core.image
import zeit.web.core.template
import zeit.web.core.utils
import zeit.web.site.module.search_form


@pytest.fixture(scope='session')
def template_server_session(request):
    server = gocept.httpserverlayer.static.Layer(module=__name__)
    server.setUp()
    request.addfinalizer(server.tearDown)
    server.url = 'http://%s' % server['http_address']
    return server


@pytest.fixture
def template_server(template_server_session):
    template_server_session.testSetUp()
    return template_server_session


def test_retrieves_template_via_http(template_server):
    open(template_server['documentroot'] + '/foo.html', 'w').write('foo')

    loader = zeit.web.core.jinja.HTTPLoader(template_server.url)
    source, path, uptodate = loader.get_source(None, 'foo.html')
    assert 'foo' == source


def test_checks_uptodate_using_last_modified_header(template_server):
    template = template_server['documentroot'] + '/foo.html'
    open(template, 'w').write('foo')

    loader = zeit.web.core.jinja.HTTPLoader(template_server.url)
    source, path, uptodate = loader.get_source(None, 'foo.html')

    assert uptodate()
    later = time.time() + 1
    os.utime(template, (later, later))
    assert not uptodate()


def test_no_url_configured_yields_error_message():
    loader = zeit.web.core.jinja.HTTPLoader(url=None)
    source, path, uptodate = loader.get_source(None, 'foo.html')
    assert 'load_template_from_dav_url' in source


def test_get_teaser_image(testserver):
    teaser_block = mock.MagicMock()
    teaser_block.layout.image_pattern = 'zmo-large'
    teaser = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/article_video_asset'
    )
    image = zeit.web.core.template.get_teaser_image(teaser_block, teaser)
    assert isinstance(image, zeit.web.core.image.TeaserImage), (
        'Article with video asset should produce a teaser image.')
    assert 'katzencontent-zmo-large.jpg' in image.src

    teaser = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de'
        '/zeit-magazin/test-cp-legacy/kochen-wuerzen-veganer-kuchen'
    )

    image = zeit.web.core.template.get_teaser_image(teaser_block, teaser)
    assert isinstance(image, zeit.web.core.image.TeaserImage), (
        'Article with image asset should produce a teaser image.')
    assert 'frau-isst-suppe-2-zmo-large.jpg' in image.src


def test_get_teaser_image_should_set_image_pattern(testserver):
    teaser_block = mock.MagicMock()
    teaser_block.layout.image_pattern = 'zmo-large'
    teaser = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/article_video_asset'
    )
    image = zeit.web.core.template.get_teaser_image(teaser_block, teaser)
    assert image.image_pattern == 'zmo-large'


def test_get_teaser_image_should_utilize_unique_id(testserver):
    teaser_block = mock.MagicMock()
    teaser_block.layout.image_pattern = 'zmo-large'
    teaser = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/article_video_asset'
    )
    unique_id = 'http://xml.zeit.de/centerpage/katzencontent/'
    image = zeit.web.core.template.get_teaser_image(
        teaser_block, teaser, unique_id=unique_id)
    assert image.uniqueId == (
        'http://xml.zeit.de/centerpage/'
        'katzencontent/katzencontent-zmo-large.jpg')


def test_get_teaser_image_should_catch_fictitious_unique_id(testserver):
    teaser_block = mock.MagicMock()
    teaser_block.layout.image_pattern = 'zmo-large'
    teaser = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/article_video_asset'
    )
    unique_id = 'http://xml.zeit.de/moep/moepmoep/moep'
    image = zeit.web.core.template.get_teaser_image(
        teaser_block, teaser, unique_id=unique_id)
    assert image is None


def test_get_teaser_image_should_utilize_fallback_image(testserver):
    teaser_block = mock.MagicMock()
    teaser_block.layout.image_pattern = 'zmo-large'
    teaser = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/artikel/artikel-ohne-assets'
    )
    image = zeit.web.core.template.get_teaser_image(
        teaser_block, teaser)
    assert image.uniqueId == (
        'http://xml.zeit.de/zeit-magazin/'
        'default/teaser_image/teaser_image-zmo-large.jpg')


def test_get_teaser_image_should_render_fallback_for_broken_image(testserver):
    teaser_block = mock.MagicMock()
    teaser_block.layout.image_pattern = 'zmo-large'
    teaser = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/article_with_broken_image_asset'
    )
    image = zeit.web.core.template.get_teaser_image(
        teaser_block, teaser)
    assert image.uniqueId == (
        'http://xml.zeit.de/zeit-magazin/'
        'default/teaser_image/teaser_image-zmo-large.jpg')


def test_jinja_env_registrator_registers_only_after_scanning(testserver):
    jinja = mock.Mock()
    jinja.foo = {}

    register_foo = zeit.web.core.decorator.JinjaEnvRegistrator('foo')
    do_foo = register_foo(lambda: 42)
    globals()['do_foo'] = do_foo

    assert do_foo() == 42
    assert jinja.foo == {}

    scanner = venusian.Scanner(env=jinja)
    scanner.scan(sys.modules[__name__], categories=('jinja',),)

    assert do_foo() == 42
    assert 'do_foo' in jinja.foo


def test_get_teaser_image_should_determine_mimetype_autonomously(testserver):
    teaser_block = mock.MagicMock()
    teaser_block.layout.image_pattern = 'zmo-card-flip-flip'
    teaser = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp-legacy/card-flip-flip'
    )
    image = zeit.web.core.template.get_teaser_image(teaser_block, teaser)
    assert image.uniqueId.split('.')[-1] == 'png'

    teaser_block.layout.image_pattern = 'zmo-card-picture'
    teaser = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp-legacy/card-picture'
    )
    image = zeit.web.core.template.get_teaser_image(teaser_block, teaser)
    assert image.uniqueId.split('.')[-1] == 'jpg'


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


def test_teaser_layout_should_be_cached_per_unique_id(application):
    block = mock.Mock()
    block.__iter__ = lambda _: iter(['article'])
    block.layout.id = 'zon-small'
    block.__hash__ = lambda _: 42

    request = mock.Mock()
    request.teaser_layout = {}
    teaser = zeit.web.core.template.get_layout(block, request=request)
    assert teaser == 'zon-small'
    assert request.teaser_layout[42] == 'zon-small'

    request = mock.Mock()
    request.teaser_layout.get = mock.Mock(return_value='zon-small')

    teaser = zeit.web.core.template.get_layout(block, request=request)
    assert teaser == 'zon-small'
    request.teaser_layout.get.assert_called_with(42, None)


def test_get_layout_should_deal_with_all_sort_of_unset_params(
        application):

    block = mock.Mock()
    block.__iter__ = lambda _: iter(['article'])
    block.layout.id = 'zon-small'

    request = mock.Mock()
    request.teaser_layout = None

    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-small'

    teaser = zeit.web.core.template.get_layout(block, request=request)
    assert teaser == 'zon-small'

    request = mock.Mock()
    request.teaser_layout = {}
    block.uniqueId = None

    teaser = zeit.web.core.template.get_layout(block, request=request)
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


def test_teaser_layout_zon_square_should_be_adjusted_accordingly(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/feature/feature_longform')
    block = mock.Mock()
    block.layout.id = 'zon-square'
    block.__parent__ = mock.Mock()
    block.__parent__.kind = 'major'
    block.__iter__ = lambda _: iter([article])
    layout = zeit.web.core.template.get_layout(block)
    assert layout == 'zon-square'

    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    block.__iter__ = lambda _: iter([article])
    layout = zeit.web.core.template.get_layout(block)
    assert layout == 'zmo-square'


def test_teaser_layout_for_series_on_zmo_cps_should_remain_untouched(
        application, monkeypatch):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/04')
    monkeypatch.setattr(zeit.content.cp.interfaces,
                        'ICenterPage', lambda *_: article)
    block = mock.MagicMock()
    block.layout.id = 'zmo-square-large'
    block.__iter__.return_value = iter([article])
    block.__parent__ = mock.Mock()
    block.__parent__.kind = 'major'
    layout = zeit.web.core.template.get_layout(block)
    assert layout == 'zmo-square-large'


def test_function_get_image_pattern_is_working_as_expected(application):
    # Existing formats
    teaser = zeit.web.core.template.get_image_pattern('zon-large', 'default')
    assert teaser == ['zon-large', '540x304']
    teaser = zeit.web.core.template.get_image_pattern('zon-small', 'default')
    assert teaser == ['zon-thumbnail', '540x304']

    # Non existing format, returns default
    teaser = zeit.web.core.template.get_image_pattern(
        'zon-large-none', 'default')
    assert teaser == ['default']


def test_visual_profiler_should_not_interfere_with_rendering_if_disabled(
        testbrowser):
    browser = testbrowser('/zeit-online/slenderized-index')
    assert not len(browser.cssselect('div.__pro__'))

    browser = testbrowser('/zeit-magazin/index')
    assert not len(browser.cssselect('div.__pro__'))


def test_visual_profiler_should_inject_performance_visualization(application):
    # XXX I couldn't defeat isolation issues to do a full integration test
    #     with the profiler extension :pensive:
    #     So this is a very basic (but isolated) test setup. (ND)

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['jinja2.enable_profiler'] = 'True'

    def world():
        return __import__('time').sleep(0.1) or 'world'

    env = jinja2.Environment()
    env.add_extension(zeit.web.core.jinja.ProfilerExtension)
    tpl = env.from_string(
        '{% profile %}Hello {{ world() }}{% endprofile%}',
        {'world': world})

    document = lxml.html.fromstring(tpl.render())

    assert len(document.cssselect('div.__pro__')) == 1
    assert document.cssselect('div.__pro__')[0].text == 'Hello world'
    assert int(document.cssselect('div.__pro__ b')[0].text.rstrip('ms'))


@pytest.mark.parametrize('expr, value', [('True', 'bar'), ('False', '')])
def test_require_extension_should_only_execute_if_expr_evaluates_to_true(
        jinja2_env, expr, value):
    tpl = '{% require foo = ' + expr + ' %} bar {% endrequire %}'
    assert jinja2_env.from_string(tpl).render().strip() == value


def test_require_extension_should_ensure_variable_access_in_inner_block(
        jinja2_env):
    tpl = '{% require foo = "pre" + fix %} {{ foo }} {% endrequire %}'
    assert jinja2_env.from_string(tpl).render(fix='fix').strip() == 'prefix'


def test_get_column_image_should_return_an_image_or_none(application):
    img = zeit.web.core.template.get_column_image(
        zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/zeit-online/cp-content/kolumne'))

    assert isinstance(img, zeit.web.core.image.VariantImage)
    assert zeit.web.core.template.get_column_image(None) is None

    teaser = mock.Mock()
    teaser.authorships = None
    assert zeit.web.core.template.get_column_image(teaser) is None


def test_debug_breaking_news_request(testbrowser):
    browser = testbrowser('/zeit-online/slenderized-index?debug=eilmeldung')
    assert browser.cssselect('.breaking-news-banner')


def test_debug_breaking_news_default(testbrowser):
    browser = testbrowser('/zeit-online/slenderized-index')
    assert not browser.cssselect('.breaking-news-banner')


def test_attr_safe_returns_safe_text(application):
    text = u'10 Saurier sind super % auf Zack'
    target = 'sauriersindsuperaufzack'
    assert zeit.web.core.template.attr_safe(text) == target


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
    request.path_url = 'http://example.com'
    request.GET = {}
    get_params = {'newparam': 'foo'}
    assert 'http://example.com?newparam=foo' == (
        zeit.web.core.template.append_get_params(request, **get_params))


def test_filter_append_get_params_should_append_params():
    request = mock.Mock()
    request.path_url = 'http://example.com'
    request.GET = {u'key1': u'1'}
    get_params = {'newparam': 'foo'}
    assert 'http://example.com?key1=1&newparam=foo' == (
        zeit.web.core.template.append_get_params(request, **get_params))


def test_filter_append_get_params_should_keep_not_overridden_params():
    request = mock.Mock()
    request.path_url = 'http://example.com'
    request.GET = webob.multidict.MultiDict(
        [(u'key1', u'1'), (u'key1', u'2')])
    get_params = {'newparam': 'foo'}
    assert 'http://example.com?key1=1&key1=2&newparam=foo' == (
        zeit.web.core.template.append_get_params(request, **get_params))


def test_filter_append_get_params_should_reset_params():
    request = mock.Mock()
    request.path_url = 'http://example.com'
    request.GET = {u'key1': u'1', u'key2': u'2'}
    get_params = {u'key1': None}
    assert 'http://example.com?key2=2' == (
        zeit.web.core.template.append_get_params(request, **get_params))


def test_filter_append_get_params_should_accept_unicode():
    request = mock.Mock()
    request.path_url = 'http://example.com'
    request.GET = {u'sören_mag': u'käse'}
    assert u'http://example.com?s%C3%B6ren_mag=k%C3%A4se' == (
        zeit.web.core.template.append_get_params(request))


def test_get_module_filter_should_correctly_extract_cpextra_id(application):
    block = object()
    assert zeit.web.core.template.get_module(block) is block

    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/suche/index')
    block = zeit.web.core.utils.find_block(cp, module='search-form')

    block.cpextra = 'n/a'
    module = zeit.web.core.template.get_module(block)
    assert isinstance(module, zeit.web.core.centerpage.Module)
    assert module.layout.id == 'n/a'

    block.cpextra = 'search-form'
    module = zeit.web.core.template.get_module(block)
    assert isinstance(module, zeit.web.site.module.search_form.Form)
    assert module.layout.id == 'search-form'


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


@pytest.mark.parametrize('patterns', itertools.permutations(
                         ['540x304', '368x220', '148x84']))
def test_existing_image_should_preserve_pattern_order(
        patterns, application, monkeypatch):
    group = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/exampleimages/artikel/01/schoppenstube/')
    monkeypatch.setattr(
        group, 'keys',
        lambda: [u'schoppenstube-540x304.jpg', u'schoppenstube-148x84.jpg'])
    image, pattern = zeit.web.core.template._existing_image(
        group, patterns, 'jpg')
    expected_pattern = (lambda x: x.remove('368x220') or x)(list(patterns))[0]
    assert pattern == expected_pattern


def test_join_if_exists_should_should_filter_none():
    assert zeit.web.core.template.join_if_exists(
        ['honey', None, 'flash'], '-') == 'honey-flash'
