# -*- coding: utf-8 -*-
import jinja2
import mock
import pytest
import zope.component

from zeit.content.video.video import VideoRendition
import zeit.cms.interfaces
import zeit.content.video.interfaces

from zeit.web.core.block import Video


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
    video = Video(model_block)

    player = zope.component.getUtility(zeit.content.video.interfaces.IPlayer)
    with mock.patch.object(player, 'get_video') as get_video:
        get_video.return_value = {
            'video_still': None,
            'thumbnail': None,
            'renditions': [rend_1, rend_2, rend_3]
        }

        assert video.highest_rendition_url == "http://rend_2"

        get_video.return_value['renditions'] = ()
        assert video.highest_rendition_url is None


@pytest.mark.parametrize('layout, klass', [
    ('', 'figure is-constrained is-centered'),
    ('zmo-small-left', 'figure-stamp'),
    ('zmo-small-right', 'figure-stamp--right'),
    ('zmo-large-center', 'figure-full-width'),
    ('large', 'figure-full-width'),
    ('zmo-small-left', 'figure-stamp'),
    ('small', 'figure-stamp')]
)
def test_video_block_should_produce_markup(layout, klass, tplbrowser):
    block = {'id': 42, 'video_still': 'pic.jpg', 'video': 'fake',
             'subtitle': 'test', 'layout': layout, 'title': 'title'}
    view = {'package': 'zeit.web.magazin'}

    browser = tplbrowser(
        'zeit.web.magazin:templates/inc/blocks/video.html',
        block=block, view=view)

    figure = browser.cssselect('figure')[0]
    assert figure.get('class').strip() == klass
    assert figure.get('data-video-provider') == 'brightcove'

    video = browser.cssselect('video')[0]
    assert video.get('data-video-id') == '42'
    assert video.get('class') == 'video-js video-player__videotag'

    caption = browser.cssselect('figcaption')[0]
    assert caption.get('class') == 'figure__caption'
    assert caption.text.strip() == 'test'


def test_headervideo_block_should_produce_markup(tplbrowser):
    block = {'highest_rendition_url': 'test.mp4', 'id': 42,
             'video_still': 'pic.jpg'}

    browser = tplbrowser(
        'zeit.web.magazin:templates/inc/blocks/video_longform.html',
        block=block)

    assert browser.cssselect('div')[0].get('data-backgroundvideo') == '42'
    assert browser.cssselect('video')[0].get('poster') == 'pic.jpg'
    assert browser.cssselect('source')[0].get('src') == 'test.mp4'
    assert browser.cssselect('source')[1].get('src') == (
        'https://live0.zeit.de/multimedia/videos/42.webm')
    assert browser.cssselect('img')[0].get('src') == (
        'https://live0.zeit.de/multimedia/videos/42.jpg')


def test_headervideo_block_should_handle_video_id_correctly(tplbrowser):
    tpl = 'zeit.web.magazin:templates/inc/blocks/video_longform.html'
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
