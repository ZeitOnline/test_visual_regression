from zeit.frontend.block import _inline_html
from zeit.frontend.block import Video
from zeit.frontend.block import HeaderVideo
from zeit.frontend.block import Image
from zeit.frontend.block import HeaderImage
import lxml.etree
import mock


def test_inline_html_should_filter_to_valid_html():
    p = """
           <p>Text <a href='foo' class='myclass' rel='nofollow' data-foo='bar' foo='ron'> ba </a> und <em>Text</em>
           abc <invalid>invalid</invalid> valid: <em>valid</em></p>
       """

    xml = lxml.etree.fromstring(p)
    xml_str = """Text <a href="foo" class="myclass" rel="nofollow" data-foo="bar"> ba </a> und <em>Text</em>
           abc invalid valid: <em>valid</em>
"""
    print _inline_html(xml)
    assert xml_str == str(_inline_html(xml))


def test_inline_html_should_return_none_on_non_xml_input():
    assert _inline_html('foo') is None
    assert _inline_html(None) is None


def test_video_block_should_be_fault_tolerant_if_video_is_None():
    model_block = mock.Mock()
    model_block.video = None
    video = Video(model_block)
    assert not hasattr(video, 'video_still')

    model_block = mock.Mock()
    model_block.video.uniqueId = 'foo'
    video = Video(model_block)
    assert hasattr(video, 'video_still')


def test_header_video_should_be_created_if_layout_is_zmo_header():
    model_block = mock.Mock()
    model_block.layout = 'zmo-xl-header'
    model_block.video.uniqueId = 'foo'
    h_video = HeaderVideo(model_block)
    assert type(h_video) == HeaderVideo
    assert h_video.format == 'zmo-xl-header'


def test_header_video_should_not_be_created_if_layout_does_not_fit():
    model_block = mock.Mock()
    model_block.layout = 'zmo-xl-noheader'
    model_block.video.uniqueId = 'foo'

    h_video = HeaderVideo(model_block)
    assert h_video == None


def test_header_image_should_be_created_if_layout_is_zmo_header():
    model_block = mock.Mock()
    model_block.layout = 'zmo-xl-header'
    model_block.is_empty = None
    h_image = HeaderImage(model_block)
    assert type(h_image) == HeaderImage


def test_header_image_should_not_be_created_if_layout_does_not_fit():
    model_block = mock.Mock()
    model_block.layout = 'zmo-xl-noheader'
    model_block.is_empty = None

    h_image = HeaderImage(model_block)
    assert h_image == None

def test_image_should_be_None_if_is_empty_is_True():
    model_block = mock.Mock()
    model_block.layout = 'zmo-xl-noheader'
    model_block.is_empty = True
    image = Image(model_block)
    assert image == None

def test_image_should_be_Fail_if_is_empty_doesnot_exist():
    model_block = mock.Mock()
    model_block.layout = 'zmo-xl-header'
    model_block.is_empty = None
    image = Image(model_block)
    assert image == None

