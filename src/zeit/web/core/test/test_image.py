# -*- coding: utf-8 -*-
from hashlib import sha1
from StringIO import StringIO

from PIL import Image
from pytest import mark
import requests

import zeit.cms.interfaces


def test_image_download(appbrowser):
    path = '/politik/deutschland/2013-07/bnd/bnd-148x84.jpg'
    result = appbrowser.get(path)
    image = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/' + path)
    assert ''.join(result.app_iter) == image.open().read()
    assert result.headers['Content-Length'] == '4843'
    assert result.headers['Content-Type'] == 'image/jpeg'
    assert result.headers['Content-Disposition'] == (
        'inline; filename="bnd-148x84.jpg"')


def test_scaled_image_download(appbrowser):
    path = '/politik/deutschland/2013-07/bnd/bnd-148x84.jpg'
    signature = sha1('80:60:time').hexdigest()  # We know the secret! :)
    result = appbrowser.get('/bitblt-80x60-' + signature + path)
    image = Image.open(StringIO(''.join(result.app_iter)))
    assert image.size == (80, 60)
    assert int(result.headers['Content-Length']) < 4843
    assert result.headers['Content-Type'] == 'image/jpeg'
    assert result.headers['Content-Disposition'] == (
        'inline; filename="bnd-148x84.jpg"')


def test_scaled_image_download_with_bad_signature(appbrowser):
    path = '/politik/deutschland/2013-07/bnd/bnd-148x84.jpg'
    signature = sha1('80:60:foobar').hexdigest()  # We know the secret! :)
    result = appbrowser.get('/bitblt-80x60-' + signature + path)
    # Bad signatures cause `repoze.bitblt` to do nothing;
    # we get the original image.
    image = Image.open(StringIO(''.join(result.app_iter)))
    assert image.size == (148, 84)
    assert result.headers['Content-Length'] == '4843'


@mark.parametrize('pattern,length', [('still', 448340), ('thumbnail', 20936)])
def test_image_download_from_brightcove_assets(pattern, length, appbrowser):
    path = '/video/2014-01/3035864892001'
    result = appbrowser.get('{}/imagegroup/{}.jpg'.format(path, pattern))
    group = zeit.content.image.interfaces.IImageGroup(
        zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de{}'.format(path)))
    image = group['{}.jpg'.format(pattern)].image
    assert ''.join(result.app_iter) == image.open().read()
    assert result.headers['Content-Length'] == str(length)
    assert result.headers['Content-Type'] == 'image/jpeg'
    assert result.headers['Content-Disposition'] == (
        'inline; filename="{}.jpg"'.format(pattern))


@mark.parametrize('pattern', ['still', 'thumbnail'])
def test_scaled_image_download_from_brightcove_assets(pattern, appbrowser):
    path = '/video/2014-01/3089721834001'
    signature = sha1('80:60:time').hexdigest()  # We know the secret! :)
    result = appbrowser.get(
        '{}/imagegroup/bitblt-80x60-{}/{}.jpg'.format(path, signature, pattern)
    )
    image = Image.open(StringIO(''.join(result.app_iter)))
    assert image.size == (80, 60)
    assert result.headers['Content-Type'] == 'image/jpeg'
    assert result.headers['Content-Disposition'] == (
        'inline; filename="{}.jpg"'.format(pattern))


@mark.parametrize('pattern', ['still', 'thumbnail'])
def test_brightcove_images_should_set_caching_headers(
        pattern, testserver, app_settings):
    resp = requests.get(
        '{}/video/2014-01/3089721834001/imagegroup/{}.jpg'.format(
            testserver.url, pattern))
    assert resp.headers.get('Cache-Control') == 'max-age={}'.format(
        app_settings.get('caching_time_videostill'))


def test_native_images_should_set_caching_headers(testserver, app_settings):
    resp = requests.get(
        '{}/zeit-online/cp-content/ig-1/ig-1-zon-fullwidth.jpg'.format(
            testserver.url))
    assert resp.headers.get('Cache-Control') == 'max-age={}'.format(
        app_settings.get('caching_time_image'))


def test_spektrum_images_should_set_caching_headers(testserver, app_settings):
    resp = requests.get('{}/spektrum-image/images/img1.jpg'.format(
        testserver.url))
    assert resp.headers.get('Cache-Control') == 'max-age={}'.format(
        app_settings.get('caching_time_external'))


def test_variant_image_should_provide_desired_attributes(application):
    group = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/ig-4')
    meta = zeit.content.image.interfaces.IImageMetadata(group)
    variant = group.get_variant_by_key('default')
    img = zeit.web.core.interfaces.ITeaserImage(variant)

    assert img.alt == img.attr_alt == meta.alt
    assert img.title == img.attr_title == meta.title
    assert img.caption == meta.caption
    assert img.copyright == meta.copyrights
    assert img.image_pattern == img.variant == variant.name
    assert img.ratio == variant.ratio
    assert img.path == 'zeit-online/cp-content/ig-4/default'


def test_variant_jinja_test_should_recognize_variants(application):
    assert zeit.web.core.template.variant(42) is False

    group = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/ig-4')
    variant = group.get_variant_by_key('default')
    img = zeit.web.core.interfaces.ITeaserImage(variant)

    assert zeit.web.core.template.variant(img) is True


def test_variant_getter_should_fallback_to_fallback_if_fallback_is_enabled(
        application):
    pass


def test_variant_getter_should_fallback_to_fallback_if_fallback_is_disabled(
        application):
    pass


def test_variant_getter_should_favour_provided_image_over_extracted(
        application):
    pass


def test_variant_getter_should_extract_image_if_not_explicitly_provided(
        application):
    pass


def test_variant_getter_should_bail_if_provided_content_has_no_image(
        application):
    pass


def test_variant_getter_should_bail_if_extracted_content_has_no_image(
        application):
    pass


def test_variant_getter_should_know_how_to_extrawurst_nextread_modules(
        application):
    pass


def test_variant_getter_should_extract_image_pattern_from_a_provided_module(
        application):
    pass


def test_variant_getter_should_default_to_default_pattern_if_pattern_invalid(
        application):
    pass


def test_variant_getter_should_get_correct_variant_by_image_pattern(
        application):
    pass


def test_variant_getter_should_gracefully_handle_unavailable_variant(
        application):
    pass


def test_variant_getter_should_output_a_variant_image_if_all_went_well(
        application):
    pass
