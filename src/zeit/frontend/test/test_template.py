import os
import time

import gocept.httpserverlayer.static
import mock
import pytest

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


def test_substitute_image_returns_empty_if_image_group_not_provided(
        application):
    assert not zeit.frontend.template.closest_substitute_image(
        'no_img_group', 'no_img_pattern')


def test_substitute_image_returns_pattern_on_exact_match(
        application, image_group_factory):
    image_group = image_group_factory(small=(150, 150))
    assert zeit.frontend.template.closest_substitute_image(
        image_group, 'small') == image_group.get('small')


def test_substitute_image_returns_empty_if_pattern_is_invalid(
        application, image_group_factory):
    assert not zeit.frontend.template.closest_substitute_image(
        image_group_factory(), 'moep')


def test_substitue_image_returns_empty_on_candidate_shortage(
        application, image_group_factory):
    assert not zeit.frontend.template.closest_substitute_image(
        image_group_factory(), 'zmo-small')
    assert not zeit.frontend.template.closest_substitute_image(
        image_group_factory(small=(90, 30)), 'zmo-square-small',
        force_orientation=True)


def test_substitute_image_returns_closest_match_within_image_group(
        application, image_group_factory):
    image_group = image_group_factory(foo=(148, 102), moo=(142, 142),
                                      boo=(350, 500), meh=(90, 146))
    assert 'boo' in zeit.frontend.template.closest_substitute_image(
        image_group, 'zmo-lead-upright')
    assert 'moo' in zeit.frontend.template.closest_substitute_image(
        image_group, 'zmo-square-small', force_orientation=True)
