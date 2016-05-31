# -*- coding: utf-8 -*-
from mock import Mock

from zeit.content.video.video import VideoRendition
import zeit.cms.interfaces

from zeit.web.core.block import HeaderVideo
from zeit.web.core.block import Video


def test_video_html(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/01' % testserver.url)
    for video in driver.find_elements_by_tag_name('figure'):
        if video.get_attribute("data-video"):
            still = video.find_element_by_class_name("video__still")
            img = video.find_element_by_tag_name("img")
            button = video.find_element_by_css_selector(".video__button")
            caption = video.find_element_by_tag_name("figcaption")
            # before click
            assert still.tag_name == 'div'
            assert 'figure__media' == unicode(img.get_attribute("class"))
            assert 'figure__caption' == unicode(caption.get_attribute("class"))
            # after click
            button.click()
            wrap = video.find_element_by_class_name("video__wrapper")
            try:
                wrap.find_element_by_tag_name("object")
            except:
                wrap.find_element_by_tag_name("iframe")
            # test if the correct video is shown
            assert wrap.get_attribute(
                "data-video") == video.get_attribute("data-video")


def test_video_source_should_be_highest_rendition_url(application):
    model_block = Mock()
    model_block.layout = 'zmo-small-left'
    rend_1 = VideoRendition()
    rend_1.frame_width = 460
    rend_1.url = "http://rend_1"

    rend_2 = VideoRendition()
    rend_2.frame_width = 1860
    rend_2.url = "http://rend_2"

    rend_3 = VideoRendition()
    rend_3.frame_width = 1260
    rend_3.url = "http://rend_3"
    model_block.video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/video/3537342483001')

    model_block.video.renditions = [rend_1, rend_2, rend_3]
    video = Video(model_block)

    assert video.highest_rendition == "http://rend_2"

    model_block.video.renditions = ()
    video = Video(model_block)
    assert video.highest_rendition is None


def test_header_video_should_be_created_if_layout_is_zmo_header(application):
    model_block = Mock()
    model_block.layout = 'zmo-xl-header'
    model_block.video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/video/3537342483001')
    h_video = HeaderVideo(model_block)
    assert type(h_video) == HeaderVideo
    assert h_video.format == 'zmo-xl-header'

    model_block = Mock()
    model_block.layout = 'zmo-small-left'
    model_block.video.uniqueId = 'foo'

    h_video = HeaderVideo(model_block)
    assert h_video is None
