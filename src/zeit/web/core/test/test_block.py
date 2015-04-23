# -*- coding: utf-8 -*-
import lxml.etree
import mock

import zeit.web.core.block


def test_inline_html_should_filter_to_valid_html():
    p = ('<p>Text <a href="foo" class="myclass" rel="nofollow" '
         'data-foo="bar"> ba </a> und <em>Text</em> abc invalid valid: '
         '<em>valid</em></p>')

    xml = lxml.etree.fromstring(p)
    xml_str = ('Text <a href="foo" class="myclass" rel="nofollow" '
               'data-foo="bar"> ba </a> und <em>Text</em> abc invalid valid: '
               '<em>valid</em>')

    assert xml_str == (
        str(zeit.web.core.block._inline_html(xml)).replace('\n', ''))


def test_inline_html_should_return_none_on_non_xml_input():
    assert zeit.web.core.block._inline_html('foo') is None
    assert zeit.web.core.block._inline_html(None) is None


def test_video_block_should_be_fault_tolerant_if_video_is_none():
    model_block = mock.Mock()
    model_block.video = None
    video = zeit.web.core.block.Video(model_block)
    assert not hasattr(video, 'video_still')

    model_block = mock.Mock()
    model_block.video.uniqueId = 'foo'
    video = zeit.web.core.block.Video(model_block)
    assert hasattr(video, 'video_still')


def test_header_video_should_be_created_if_layout_is_zmo_header():
    model_block = mock.Mock()
    model_block.layout = 'zmo-xl-header'
    model_block.video.uniqueId = 'foo'
    h_video = zeit.web.core.block.HeaderVideo(model_block)
    assert type(h_video) == zeit.web.core.block.HeaderVideo
    assert h_video.format == 'zmo-xl-header'


def test_header_video_should_not_be_created_if_layout_does_not_fit():
    model_block = mock.Mock()
    model_block.layout = 'zmo-xl-noheader'
    model_block.video.uniqueId = 'foo'

    h_video = zeit.web.core.block.HeaderVideo(model_block)
    assert h_video is None


def test_header_image_should_be_created_if_layout_is_zmo_header():
    model_block = mock.Mock()
    model_block.layout = 'zmo-xl-header'
    model_block.is_empty = False
    h_image = zeit.web.core.block.HeaderImage(model_block)
    assert type(h_image) == zeit.web.core.block.HeaderImage


def test_header_image_should_not_be_created_if_layout_does_not_fit():
    model_block = mock.Mock()
    model_block.layout = 'zmo-xl-noheader'
    model_block.is_empty = False

    h_image = zeit.web.core.block.HeaderImage(model_block)
    assert h_image is None


def test_image_should_be_none_if_is_empty_is_true():
    model_block = mock.Mock()
    model_block.layout = 'zmo-xl-noheader'
    model_block.is_empty = True
    image = zeit.web.core.block.Image(model_block)
    assert image is None


def test_image_should_be_fail_if_is_empty_doesnot_exist():
    model_block = mock.Mock(spec=('layout',))
    model_block.layout = 'zmo-xl-header'
    model_block.is_empty = None
    image = zeit.web.core.block.Image(model_block)
    assert image is None
