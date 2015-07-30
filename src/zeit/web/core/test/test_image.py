# -*- coding: utf-8 -*-
from hashlib import sha1
from StringIO import StringIO

from PIL import Image
from pytest import mark
import mock
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
    variant = zeit.web.core.template.get_image(None, fallback=True)
    assert variant.image_group.uniqueId.endswith('/default/teaser_image/')


def test_variant_getter_should_fallback_to_fallback_if_fallback_is_disabled(
        application):
    variant = zeit.web.core.template.get_image(None, fallback=False)
    assert variant is None


def test_variant_getter_should_favour_provided_content_over_extracted(
        application):
    module = [zeit.cms.interfaces.ICMSContent(
              'http://xml.zeit.de/zeit-online/cp-content/article-01')]
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/article-02')
    variant = zeit.web.core.template.get_image(module, content)
    assert variant.path.endswith('default')


def test_variant_getter_should_extract_content_if_not_explicitly_provided(
        application):
    module = [zeit.cms.interfaces.ICMSContent(
              'http://xml.zeit.de/zeit-online/cp-content/article-01')]
    variant = zeit.web.core.template.get_image(module)
    assert variant.path.endswith('default')


def test_variant_getter_should_bail_if_provided_content_has_no_image(
        application):
    variant = zeit.web.core.template.get_image([], mock.Mock(), False)
    assert variant is None


def test_variant_getter_should_bail_if_extracted_content_has_no_image(
        application):
    variant = zeit.web.core.template.get_image(mock.Mock(), None, False)
    assert variant is None


def test_variant_getter_should_know_how_to_extrawurst_nextread_modules(
        application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/article-01')
    module = zeit.web.core.block.ZONNextread([content])
    variant = zeit.web.core.template.get_image(module)
    assert variant.path.endswith('cinema')


def test_variant_getter_should_extract_image_pattern_from_a_provided_module(
        application, monkeypatch):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/article-01')
    monkeypatch.setattr(zeit.web.core.template, 'get_layout', 'large'.format)
    variant = zeit.web.core.template.get_image(mock.Mock(), content)
    assert variant.path.endswith('wide')


def test_variant_getter_should_default_to_default_pattern_if_pattern_invalid(
        application, monkeypatch):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/article-01')
    monkeypatch.setattr(zeit.web.core.template, 'get_layout', 'foobar'.format)
    variant = zeit.web.core.template.get_image(mock.Mock(), content)
    assert variant.path.endswith('default')


def test_variant_getter_should_get_correct_variant_by_image_pattern(
        application, monkeypatch):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/article-01')
    monkeypatch.setattr(zeit.web.core.template, 'get_layout', 'large'.format)
    variant = zeit.web.core.template.get_image(mock.Mock(), content)
    imagegroup = zeit.content.image.interfaces.IImages(content).image
    assert imagegroup.get_variant_by_key('wide') == variant.context


def test_variant_getter_should_gracefully_handle_unavailable_variant(
        application, monkeypatch):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/article-01')
    monkeypatch.setattr(zeit.content.cp.layout, 'get_layout', mock.MagicMock())
    variant = zeit.web.core.template.get_image(mock.Mock(), content, False)
    assert variant is None


def test_variant_getter_should_output_a_variant_image_if_all_went_well(
        application, monkeypatch):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/article-01')
    monkeypatch.setattr(zeit.web.core.template, 'get_layout', 'large'.format)
    variant = zeit.web.core.template.get_image(mock.Mock(), content)
    assert isinstance(variant, zeit.web.core.centerpage.VariantImage)


def test_image_view_uses_native_filename_for_legacy_images(
        application):
    assert False


def test_image_view_uses_parents_basename_as_filename_if_available(
        application):
    assert False


def test_image_view_uses_traversed_path_segment_if_parent_unavailable(
        application):
    assert False


def test_image_view_uses_content_type_as_fileextension_if_available(
        application):
    assert False


def test_image_view_uses_jpeg_as_fileextension_if_content_type_unavailable(
        application):
    assert False


def test_image_view_should_handle_unicode_filename_and_extension(
        application):
    assert False


def test_image_view_should_handle_unicode_mime_types_correctly(
        application):
    assert False


def test_image_view_should_handle_ioerrors_on_filehandle_opening(
        application):
    assert False


def test_image_view_should_open_context_image_and_provide_filehandle(
        application):
    assert False


def test_image_view_should_calculate_content_length_of_context_image(
        application):
    assert False


def test_image_view_should_reset_file_handle_pointer_even_on_read_error(
        application):
    assert False


def test_image_view_should_set_headers_to_calculated_values(
        application):
    assert False


def test_image_view_should_create_fileiter_pyramid_response(
        application):
    assert False


def test_image_view_should_calculate_caching_time_from_image_context(
        application):
    assert False
