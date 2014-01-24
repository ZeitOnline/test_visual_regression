from zeit.frontend.block import _inline_html
from zeit.frontend.block import Video
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
