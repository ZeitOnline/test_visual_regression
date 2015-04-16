import datetime
import os
import sys
import time

import gocept.httpserverlayer.static
import mock
import pytest
import venusian

import zeit.cms.interfaces

import zeit.web.core.decorator
import zeit.web.core.template


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
        'http://xml.zeit.de/centerpage/article_video_asset_2'
    )
    image = zeit.web.core.template.get_teaser_image(teaser_block, teaser)
    assert isinstance(image, zeit.web.core.centerpage.TeaserImage), (
        'Article with video asset should produce a teaser image.')
    assert 'katzencontent-zmo-large.jpg' in image.src

    teaser = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de'
        '/zeit-magazin/test-cp/kochen-wuerzen-veganer-kuchen'
    )

    image = zeit.web.core.template.get_teaser_image(teaser_block, teaser)
    assert isinstance(image, zeit.web.core.centerpage.TeaserImage), (
        'Article with image asset should produce a teaser image.')
    assert 'frau-isst-suppe-2-zmo-large.jpg' in image.src


def test_get_teaser_image_should_set_image_pattern(testserver):
    teaser_block = mock.MagicMock()
    teaser_block.layout.image_pattern = 'zmo-large'
    teaser = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/article_video_asset_2'
    )
    image = zeit.web.core.template.get_teaser_image(teaser_block, teaser)
    assert image.image_pattern == 'zmo-large'


def test_get_teaser_image_should_utilize_unique_id(testserver):
    teaser_block = mock.MagicMock()
    teaser_block.layout.image_pattern = 'zmo-large'
    teaser = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/article_video_asset_2'
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
        'http://xml.zeit.de/centerpage/article_video_asset_2'
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


def test_substitute_image_returns_empty_if_image_group_not_provided(
        application):
    assert not zeit.web.core.template.closest_substitute_image(
        'no_img_group', 'no_img_pattern')


def test_substitute_image_returns_pattern_on_exact_match(
        application, image_group_factory):
    image_group = image_group_factory(small=(150, 150))
    assert zeit.web.core.template.closest_substitute_image(
        image_group, 'small') == image_group.get('small')


def test_substitute_image_returns_empty_if_pattern_is_invalid(
        application, image_group_factory):
    assert not zeit.web.core.template.closest_substitute_image(
        image_group_factory(), 'moep')


def test_substitue_image_returns_empty_on_candidate_shortage(
        application, image_group_factory):
    assert not zeit.web.core.template.closest_substitute_image(
        image_group_factory(), 'zmo-small')
    assert not zeit.web.core.template.closest_substitute_image(
        image_group_factory(small=(90, 30)), 'zmo-square-small',
        force_orientation=True)


def test_substitute_image_returns_closest_match_within_image_group(
        application, image_group_factory):
    image_group = image_group_factory(foo=(148, 102), moo=(142, 142),
                                      boo=(350, 500), meh=(90, 146))
    # zmo-lead-upright: (320, 480)
    # zmo-square-small: (50, 50)
    assert 'boo' in zeit.web.core.template.closest_substitute_image(
        image_group, 'zmo-lead-upright').uniqueId
    assert 'moo' in zeit.web.core.template.closest_substitute_image(
        image_group, 'zmo-square-small', force_orientation=True).uniqueId


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
        'http://xml.zeit.de/zeit-magazin/test-cp/card-flip-flip'
    )
    image = zeit.web.core.template.get_teaser_image(teaser_block, teaser)
    assert image.uniqueId.split('.')[-1] == 'png'

    teaser_block.layout.image_pattern = 'zmo-card-picture'
    teaser = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp/card-picture'
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
    block.uniqueId = 'http://unique'

    request = mock.Mock()
    request.teaser_layout = {}
    teaser = zeit.web.core.template.get_layout(block, request=request)
    assert teaser == 'zon-small'
    assert request.teaser_layout['http://unique#0'] == 'zon-small'

    request = mock.Mock()
    request.teaser_layout.get = mock.Mock(return_value='zon-small')

    teaser = zeit.web.core.template.get_layout(block, request=request)
    assert teaser == 'zon-small'
    request.teaser_layout.get.assert_called_with('http://unique#0', None)


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


def test_teaser_fullwidth_mapping_is_working_as_expected(application):
    block = mock.Mock()
    block.__iter__ = lambda _: iter(['article'])
    block.layout.id = 'leader-fullwidth'
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-fullwidth'


def test_hide_teaser_mapping_is_working_as_expected(application):
    block = mock.Mock()
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
    block.layout.id = 'parquet-verlag'
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'hide'


def test_teaser_layout_for_columns_should_be_adjusted_accordingly(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/kolumne')
    block = mock.Mock()
    block.layout.id = 'zon-small'
    block.__iter__ = lambda _: iter([article])
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-column'


def test_teaser_layout_for_series_should_be_adjusted_accordingly(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/serie_app_kritik')
    block = mock.Mock()
    block.layout.id = 'zon-small'
    block.__iter__ = lambda _: iter([article])
    teaser = zeit.web.core.template.get_layout(block)
    assert teaser == 'zon-series'


def test_function_get_image_pattern_is_working_as_expected(application):
    # Existing formats
    teaser = zeit.web.core.template.get_image_pattern('zon-large', 'default')
    assert teaser == ['zon-large']
    teaser = zeit.web.core.template.get_image_pattern('zon-small', 'default')
    assert teaser == ['zon-thumbnail', '540x304']

    # Non existing format, returns default
    teaser = zeit.web.core.template.get_image_pattern(
        'zon-large-none', 'default')
    assert teaser == ['default']


def test_visual_profiler_should_not_interfere_with_rendering(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/index' % testserver.url)
    assert not len(browser.cssselect('.__pro__'))

    browser = testbrowser('%s/zeit-magazin/index' % testserver.url)
    assert not len(browser.cssselect('.__pro__'))


def test_get_column_image_should_return_an_image_or_none(application):
    img = zeit.web.core.template.get_column_image(
        zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/zeit-online/cp-content/kolumne'))

    assert type(img) == zeit.web.core.centerpage.Image
    assert zeit.web.core.template.get_column_image(None) is None

    teaser = mock.Mock()
    teaser.authorships = None
    assert zeit.web.core.template.get_column_image(teaser) is None


def test_debug_breaking_news_should_be_enableable(testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/index' % testserver.url)
    assert not browser.cssselect('.breaking-news-banner')


def test_debug_breaking_news_should_be_disableable(testbrowser, testserver):
    browser = testbrowser(
        '%s/zeit-online/index?debug=eilmeldung' % testserver.url)
    assert browser.cssselect('.breaking-news-banner')
