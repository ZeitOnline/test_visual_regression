# -*- coding: utf-8 -*-
import jinja2
import mock
import pytest

from zeit.content.video.video import VideoRendition
import zeit.cms.interfaces

from zeit.web.core.block import Video


def test_video_html(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/article/01' % testserver.url)
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
    model_block = mock.Mock()
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


@pytest.mark.parametrize('format, klass', [
    ('', 'figure is-constrained is-centered'),
    ('zmo-small-left', 'figure-stamp'),
    ('zmo-small-right', 'figure-stamp--right'),
    ('zmo-large-center', 'figure-full-width'),
    ('large', 'figure-full-width'),
    ('zmo-small-left', 'figure-stamp'),
    ('small', 'figure-stamp')]
)
def test_video_block_should_produce_markup(format, klass, tplbrowser):
    block = {'id': 42, 'video_still': 'pic.jpg',
             'description': 'test', 'format': format, 'title': 'title'}
    view = {'package': 'zeit.web.magazin'}

    browser = tplbrowser(
        'zeit.web.magazin:templates/inc/blocks/video.html',
        block=block, view=view)

    figure = browser.cssselect('figure')[0]
    assert figure.attrib['class'].strip() == klass
    assert figure.attrib['data-video'] == '42'

    assert browser.cssselect('img')[0].attrib == {
        'class': 'figure__media',
        'src': 'pic.jpg',
        'alt': 'Video: title',
        'title': 'Video: title'}

    caption = browser.cssselect('figcaption')[0]
    assert caption.attrib['class'] == 'figure__caption'
    assert caption.text.strip() == 'test'


def test_headervideo_block_should_produce_markup(tplbrowser):
    block = {'highest_rendition': 'test.mp4', 'id': 42,
             'video_still': 'pic.jpg'}

    browser = tplbrowser(
        'zeit.web.magazin:templates/inc/blocks/headervideo.html',
        block=block)

    assert browser.cssselect('div')[0].attrib['data-backgroundvideo'] == '42'
    assert browser.cssselect('video')[0].attrib['poster'] == 'pic.jpg'
    assert browser.cssselect('source')[0].attrib['src'] == 'test.mp4'
    assert browser.cssselect('source')[1].attrib['src'] == (
        'http://live0.zeit.de/multimedia/videos/42.webm')
    assert browser.cssselect('img')[0].attrib['src'] == (
        'http://live0.zeit.de/multimedia/videos/42.jpg')


def test_headervideo_block_should_handle_video_id_correctly(tplbrowser):
    tpl = 'zeit.web.magazin:templates/inc/blocks/headervideo.html'
    block = mock.Mock()

    # assert empty template
    block.id = None
    block.uniqueId = None
    browser = tplbrowser(tpl, block=block)
    assert not browser.cssselect('div')

    # assert set id
    block.id = 987
    block.uniqueId = None
    browser = tplbrowser(tpl, block=block)
    assert browser.cssselect('div[data-backgroundvideo="987"]')

    # assert set uniqueid
    block.id = jinja2.Undefined()
    block.uniqueId = 'http://xml.zeit.de/video/foo/456'
    browser = tplbrowser(tpl, block=block)
    assert browser.cssselect('div[data-backgroundvideo="456"]')
