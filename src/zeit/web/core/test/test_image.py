# -*- coding: utf-8 -*-
from StringIO import StringIO

from PIL import Image
import lxml.objectify
import mock
import pyramid.httpexceptions
import pytest
import requests
import zope.interface.declarations

import zeit.cms.interfaces
import zeit.content.article.interfaces
import zeit.content.image.variant

import zeit.web.core.image
import zeit.web.core.template
import zeit.web.core.view_image


def test_original_image_download(appbrowser):
    result = appbrowser.get('/zeit-online/image/weltall/original')
    image = Image.open(StringIO(''.join(result.app_iter)))
    assert image.size == (460, 460)
    assert abs(int(result.headers['Content-Length']) - 55 * 1024) < 1024, (
        'The downloaded image should be roughly 55KB in size')
    assert result.headers['Content-Type'] == 'image/jpeg'
    assert result.headers['Content-Disposition'] == (
        'inline; filename="weltall.jpeg"')


def test_scaled_image_download(appbrowser):
    result = appbrowser.get('/zeit-online/image/weltall/wide__80x60')
    image = Image.open(StringIO(''.join(result.app_iter)))
    assert image.size == (80, 60)
    assert abs(int(result.headers['Content-Length']) - 3 * 1024) < 1024, (
        'The scaled image should be roughly 3KB in size')
    assert result.headers['Content-Type'] == 'image/jpeg'
    assert result.headers['Content-Disposition'] == (
        'inline; filename="weltall.jpeg"')


def test_synthetic_image_download(appbrowser):
    result = appbrowser.get(
        '/zeit-magazin/images/local/01.jpg/imagegroup/original')
    image = Image.open(StringIO(''.join(result.app_iter)))
    assert image.size == (580, 326)
    assert abs(int(result.headers['Content-Length']) - 33 * 1024) < 1024, (
        'The synthetic original should be roughly 33KB in size')
    assert result.headers['Content-Type'] == 'image/jpeg'
    assert result.headers['Content-Disposition'] == (
        'inline; filename="imagegroup.jpeg"')


def test_scaled_synthetic_image_download(appbrowser):
    result = appbrowser.get(
        '/zeit-magazin/images/local/01.jpg/imagegroup/wide__320x180')
    image = Image.open(StringIO(''.join(result.app_iter)))
    assert image.size == (320, 180)
    assert abs(int(result.headers['Content-Length']) - 15 * 1024) < 1024, (
        'The synthetic scale should be roughly 15KB in size')
    assert result.headers['Content-Type'] == 'image/jpeg'
    assert result.headers['Content-Disposition'] == (
        'inline; filename="imagegroup.jpeg"')


def test_image_download_from_brightcove_assets(appbrowser):
    path = '/video/2014-01/3035864892001/imagegroup/wide'
    result = appbrowser.get(path)
    group = zeit.content.image.interfaces.IImageGroup(
        zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2014-01/3035864892001'))
    assert ''.join(result.app_iter) == group['wide'].open().read()
    assert result.headers['Content-Length'] == '307690'
    assert result.headers['Content-Type'] == 'image/jpeg'
    assert result.headers['Content-Disposition'] == (
        'inline; filename="imagegroup.jpeg"')


def test_scaled_image_download_from_brightcove_assets(appbrowser):
    path = '/video/2014-01/3089721834001/imagegroup/cinema__70x30'
    result = appbrowser.get(path)
    image = Image.open(StringIO(''.join(result.app_iter)))
    assert image.size == (70, 30)
    assert result.headers['Content-Type'] == 'image/jpeg'
    assert result.headers['Content-Disposition'] == (
        'inline; filename="imagegroup.jpeg"')


def test_video_claiming_to_be_imagegroup_works_with_xmlreference(application):
    video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/video/2014-01/3035864892001')
    node = lxml.objectify.XML('<dummy/>')
    updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(video)
    # assert nothing raised
    updater.update(node, suppress_errors=True)


def test_brightcove_images_should_set_cache_headers(testserver):
    resp = requests.get(
        '{}/video/2014-01/3089721834001/imagegroup/wide'.format(
            testserver.url))
    settings = zope.component.queryUtility(zeit.web.core.interfaces.ISettings)
    assert resp.headers.get('Cache-Control') == 'max-age={}'.format(
        settings.get('caching_time_external'))


def test_native_images_should_set_cache_headers(testserver):
    resp = requests.get(
        '{}/zeit-online/cp-content/ig-1/back.jpg'.format(
            testserver.url))
    settings = zope.component.queryUtility(zeit.web.core.interfaces.ISettings)
    assert resp.headers.get('Cache-Control') == 'max-age={}'.format(
        settings.get('caching_time_image'))


def test_spektrum_images_should_set_cache_headers(testserver):
    resp = requests.get('{}/spektrum-image/images/img1.jpg/wide'.format(
        testserver.url))
    settings = zope.component.queryUtility(zeit.web.core.interfaces.ISettings)
    assert resp.headers.get('Cache-Control') == 'max-age={}'.format(
        settings.get('caching_time_external'))


def test_spektrum_images_should_handle_non_ascii(testserver):
    resp = requests.get(u'{}/spektrum-image/images/umläut.jpg/wide'.format(
        testserver.url))
    assert resp.status_code == 404


def test_image_view_uses_native_filename_for_legacy_images():
    context = mock.Mock()
    context.__name__ = 'foobar.bmp'
    context.__parent__ = ['foobar.bmp']
    context.mimeType = u'mööp'
    view = zeit.web.core.view_image.Image(context, None)
    assert view.content_disposition == 'inline; filename="foobar.bmp"'


def test_image_view_uses_parents_basename_as_filename_if_available():
    context = mock.Mock()
    context.__name__ = 'foobar.bmp'
    context.__parent__ = mock.MagicMock()
    context.__parent__.__iter__.return_value = []
    context.__parent__.uniqueId = '/lorem/ipsum/dolorset'
    context.mimeType = u'mööp'
    view = zeit.web.core.view_image.Image(context, None)
    assert view.content_disposition == 'inline; filename="dolorset.jpeg"'


def test_image_view_uses_traversed_path_segment_if_parent_unavailable():
    context = mock.Mock()
    context.__name__ = 'foobar.bmp'
    context.__parent__ = []
    context.mimeType = u'mööp'
    request = mock.Mock()
    request.path = 'lorem/ipsum'
    view = zeit.web.core.view_image.Image(context, request)
    assert view.content_disposition == 'inline; filename="ipsum.jpeg"'


def test_image_view_uses_content_type_as_fileextension_if_available():
    context = mock.Mock()
    context.__name__ = 'foobar.bmp'
    context.__parent__ = []
    context.mimeType = 'image/png'
    request = mock.Mock()
    request.path = 'dolorset'
    view = zeit.web.core.view_image.Image(context, request)
    assert view.content_disposition == 'inline; filename="dolorset.png"'


def test_image_view_uses_jpeg_as_fileextension_if_content_type_unavailable():
    context = mock.Mock()
    context.__name__ = 'foobar.bmp'
    context.__parent__ = []
    context.mimeType = u'mööp'
    request = mock.Mock()
    request.path = 'dolorset'
    view = zeit.web.core.view_image.Image(context, request)
    assert view.content_disposition == 'inline; filename="dolorset.jpeg"'


def test_image_view_should_handle_unicode_filename_and_extension():
    context = mock.Mock()
    context.__name__ = u'porträt.jpg'
    context.__parent__ = []
    context.mimeType = u'image/gemälde'
    request = mock.Mock()
    request.path = u'wunder/schönes porträt'
    view = zeit.web.core.view_image.Image(context, request)
    assert view.content_disposition == (
        'inline; filename="schoenes-portraet.jpeg"')


def test_image_view_should_handle_ioerrors_on_filehandle_opening():
    def broken_func():
        raise IOError('This file is broken!')

    context = mock.Mock()
    context.open = broken_func
    view = zeit.web.core.view_image.Image(context, mock.Mock())
    with pytest.raises(pyramid.httpexceptions.HTTPNotFound):
        view.filehandle


def test_image_view_should_open_context_image_and_provide_filehandle():
    context = mock.Mock()
    mockfile = object()
    context.open.return_value = mockfile
    view = zeit.web.core.view_image.Image(context, None)
    assert view.filehandle is mockfile
    assert context.open.call_count == 1


def test_image_view_should_calculate_content_length_of_context_image():
    context = mock.Mock()
    mockfile = mock.Mock()
    mockfile.tell.return_value = 42
    context.open.return_value = mockfile
    request = mock.Mock()
    view = zeit.web.core.view_image.Image(context, request)
    assert view.content_length == '42'
    assert mockfile.seek.call_args_list == [((0, 2), {}), ((0, 0), {})]


def test_image_view_should_reset_file_handle_pointer_even_on_read_error():
    def broken_func():
        raise IOError('This file is broken!')

    context = mock.Mock()
    mockfile = mock.Mock()
    mockfile.tell = broken_func
    context.open.return_value = mockfile
    request = mock.Mock()
    view = zeit.web.core.view_image.Image(context, request)
    assert view.content_length is None
    assert mockfile.seek.call_args == ((0, 0), {})


def test_image_view_should_set_headers_to_calculated_values(application):
    context = mock.Mock()
    context.__name__ = 'foobar.jpg'
    context.__parent__ = ['foobar.jpg']
    mockfile = mock.Mock()
    mockfile.tell.return_value = 4212345
    context.open.return_value = mockfile
    context.mimeType = 'foo/bar'
    interface = zeit.content.article.interfaces.IArticle
    zope.interface.declarations.alsoProvides(context, interface)
    request = mock.Mock()
    request.response.headers = {}
    view = zeit.web.core.view_image.Image(context, request)
    assert view().headers == {
        'Content-Disposition': 'inline; filename="foobar.jpg"',
        'Content-Length': '4212345',
        'Content-Type': "foo/bar"}


def test_image_view_should_create_fileiter_pyramid_response(application):
    context = mock.Mock()
    context.__name__ = 'foobar.jpg'
    context.__parent__ = ['foobar.jpg']
    mockfile = mock.Mock()
    context.open.return_value = mockfile
    interface = zeit.content.article.interfaces.IArticle
    zope.interface.declarations.alsoProvides(context, interface)
    request = mock.Mock()
    request.response.headers = {}
    view = zeit.web.core.view_image.Image(context, request)
    assert view().app_iter.file is mockfile


def test_image_view_should_calculate_caching_time_from_context(application):
    context = mock.Mock()
    context.__name__ = 'foobar.jpg'
    context.__parent__ = ['foobar.jpg']
    interface = zeit.content.article.interfaces.IArticle
    zope.interface.declarations.alsoProvides(context, interface)
    request = mock.Mock()
    request.response.headers = {}
    view = zeit.web.core.view_image.Image(context, request)
    assert view().cache_expires.call_args[0][0] == 10


def test_variant_source_should_produce_variant_legacy_mapping(application):
    vs = zeit.web.core.image.VARIANT_SOURCE
    assert len(vs.factory._get_mapping()) == 54


def test_variant_source_should_honor_configured_availability(
        application, monkeypatch):

    def isAvailable(self, node, context):  # NOQA
        return 'cinema' not in node.attrib['name']

    monkeypatch.setattr(
        zeit.content.image.variant.VariantSource, 'isAvailable', isAvailable)
    vs = zeit.web.core.image.VARIANT_SOURCE
    group = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/ig-1')
    assert vs.factory.find(group, 'default') is not None
    with pytest.raises(KeyError):
        vs.factory.find(group, 'cinema')


def test_variant_source_should_find_and_output_variant_instance(application):
    vs = zeit.web.core.image.VARIANT_SOURCE
    group = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/ig-1')
    variant = vs.factory.find(group, 'zmo-xl')
    assert zeit.content.image.interfaces.IVariant.providedBy(variant)


def test_variant_source_should_set_legacy_name_for_mapped_images(application):
    vs = zeit.web.core.image.VARIANT_SOURCE
    group = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/ig-1')
    variant = vs.factory.find(group, 'zmo-xl')
    assert variant.legacy_name == 'zmo-xl'


def test_variant_source_should_raise_keyerror_for_faulty_specs(application):
    vs = zeit.web.core.image.VARIANT_SOURCE
    group = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/ig-1')
    with pytest.raises(KeyError):
        vs.factory.find(group, 'extra-foo')


def test_img_src_should_contain_fallback_size(testbrowser):
    b = testbrowser('/zeit-online/slenderized-index')
    assert b.cssselect(
        'img[src$="/filmstill-hobbit-schlacht-fuenf-hee/wide__822x462"]')


def test_image_host_is_configurable_for_variant_images(testbrowser):
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    settings['image_prefix'] = 'http://img.example.com'
    b = testbrowser('/zeit-online/slenderized-index')
    assert b.cssselect('img[data-src^="http://img.example.com"]')
    assert b.cssselect('img[src^="http://img.example.com"]')


def test_image_host_is_configurable_for_legacy_images(testbrowser):
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    settings['image_prefix'] = 'http://img.example.com'
    b = testbrowser('/zeit-magazin/index')
    assert b.cssselect('img[src^="http://img.example.com"]')


def test_image_should_handle_ampersand_captions(testbrowser):
    browser = testbrowser('/feature/feature_longform')
    text = browser.xpath('//span[@class="figure__text"]')[0]
    assert u'Heckler &amp; Koch' in lxml.etree.tostring(text)
