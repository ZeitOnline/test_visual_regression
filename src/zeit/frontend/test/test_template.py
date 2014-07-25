import os
import time

import gocept.httpserverlayer.static
import mock
import pytest
import venusian

import zeit.cms.interfaces
import zeit.frontend.template


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

    loader = zeit.frontend.template.HTTPLoader(template_server.url)
    UNUSED_ENVIRONMENT = None
    source, path, uptodate = loader.get_source(UNUSED_ENVIRONMENT, 'foo.html')
    assert 'foo' == source


def test_checks_uptodate_using_last_modified_header(template_server):
    template = template_server['documentroot'] + '/foo.html'
    open(template, 'w').write('foo')

    loader = zeit.frontend.template.HTTPLoader(template_server.url)
    UNUSED_ENVIRONMENT = None
    source, path, uptodate = loader.get_source(UNUSED_ENVIRONMENT, 'foo.html')

    assert uptodate()
    later = time.time() + 1
    os.utime(template, (later, later))
    assert not uptodate()


def test_no_url_configured_yields_error_message():
    loader = zeit.frontend.template.HTTPLoader(url=None)
    UNUSED_ENVIRONMENT = None
    source, path, uptodate = loader.get_source(UNUSED_ENVIRONMENT, 'foo.html')
    assert 'load_template_from_dav_url' in source


def test_get_teaser_image(testserver):
    teaser_block = mock.MagicMock()
    teaser_block.layout.image_pattern = 'zmo-large'

    teaser = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/article_video_asset_2'
    )
    image = zeit.frontend.template.get_teaser_image(teaser_block, teaser)
    assert isinstance(image, zeit.frontend.centerpage.TeaserImage), \
        'Article with video asset should produce a teaser image.'
    assert 'katzencontent-zmo-large.jpg' in image.src

    teaser = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de'
        '/zeit-magazin/test-cp/kochen-wuerzen-veganer-kuchen'
    )
    image = zeit.frontend.template.get_teaser_image(teaser_block, teaser)
    assert isinstance(image, zeit.frontend.centerpage.TeaserImage), \
        'Article with image asset should produce a teaser image.'
    assert 'frau-isst-suppe-2-zmo-large.jpg' in image.src


def test_get_teaser_image_should_utilize_unique_id(testserver):
    teaser_block = mock.MagicMock()
    teaser_block.layout.image_pattern = 'zmo-large'
    teaser = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/article_video_asset_2'
    )
    unique_id = \
        'http://xml.zeit.de/centerpage/katzencontent/'
    image = zeit.frontend.template.get_teaser_image(
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
    unique_id = \
        'http://xml.zeit.de/moep/moepmoep/moep'
    image = zeit.frontend.template.get_teaser_image(
        teaser_block, teaser, unique_id=unique_id)
    assert image is None


def test_get_teaser_image_should_utilize_fallback_image(testserver):
    teaser_block = mock.MagicMock()
    teaser_block.layout.image_pattern = 'zmo-large'
    teaser = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/artikel/artikel-ohne-assets'
    )
    image = zeit.frontend.template.get_teaser_image(
        teaser_block, teaser)
    assert image.uniqueId == (
        'http://xml.zeit.de/zeit-magazin/'
        'default/teaser_image/teaser_image-zmo-large.jpg')


def test_jinja_env_registrator_registers_only_after_scanning(testserver):
    jinja = mock.Mock()
    jinja.foo = {}

    register_foo = zeit.frontend.template.JinjaEnvRegistrator('foo')
    do_foo = register_foo(lambda: 42)
    globals()['do_foo'] = do_foo

    assert do_foo() == 42
    assert jinja.foo == {}

    scanner = venusian.Scanner(env=jinja)
    scanner.scan(zeit.frontend.test.test_template, categories=('jinja',),)

    assert do_foo() == 42
    assert 'do_foo' in jinja.foo
