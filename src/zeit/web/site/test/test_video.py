# -*- coding: utf-8 -*-
import pytest

import zeit.cms.interfaces
import zeit.content.image.interfaces

import zeit.web.core.centerpage


def test_video_imagegroup_should_adapt_videos(application):
    video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/video/2015-01/4004256546001')
    group = zeit.content.image.interfaces.IImageGroup(video)
    assert isinstance(group, zeit.web.core.centerpage.VideoImageGroup)


def test_video_imagegroup_should_contain_two_images(application):
    video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/video/2015-01/4004256546001')
    group = zeit.content.image.interfaces.IImageGroup(video)
    assert set(group.keys()) == {'still.jpg', 'thumbnail.jpg'}


@pytest.mark.parametrize('img', ['still', 'thumbnail'])
def test_video_imagegroup_should_set_appropriate_properties(img, application):
    unique_id = 'http://xml.zeit.de/video/2015-01/4004256546001'
    video = zeit.cms.interfaces.ICMSContent(unique_id)
    group = zeit.content.image.interfaces.IImageGroup(video)
    image = group['{}.jpg'.format(img)]
    assert 'Bildschirmfoto-2015-01-22-um-09-27-07.jpg' in image.src
    assert image.mimeType == 'image/jpeg'
    assert image.image_pattern == 'brightcove-{}'.format(img)
    assert image.copyright is None
    assert image.caption.startswith(u'Er ist so groß wie ein siebenjähriges')
    assert image.title == u'Roboter Myon übernimmt Opernrolle'
    assert image.alt == u'Roboter Myon übernimmt Opernrolle'
    assert image.uniqueId == '{}/imagegroup/{}.jpg'.format(unique_id, img)


@pytest.mark.parametrize('img,size,res', [
    ('still', 460207, (580, 328)),
    ('thumbnail', 23420, (120, 67))
])
def test_video_imagegroup_should_set_local_image_fileobj(
        img, size, res, application):
    unique_id = 'http://xml.zeit.de/video/2015-01/4004256546001'
    video = zeit.cms.interfaces.ICMSContent(unique_id)
    group = zeit.content.image.interfaces.IImageGroup(video)
    image = group['{}.jpg'.format(img)]
    assert image.image.size == size
    assert image.image.getImageSize() == res
