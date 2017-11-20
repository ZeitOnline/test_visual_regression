import pytest

import zeit.cms.interfaces
import zeit.content.image.interfaces

import zeit.web.core.video


def test_video_imagegroup_should_adapt_videos(application):
    video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/video/3537342483001')
    group = zeit.content.image.interfaces.IImageGroup(video)
    assert isinstance(group, zeit.web.core.video.ImageGroup)


@pytest.mark.parametrize('img,res', [
    ('wide', (579, 326)),
    ('cinema', (580, 248))
])
def test_video_imagegroup_should_set_local_image_fileobj(
        img, res, application):
    unique_id = 'http://xml.zeit.de/zeit-online/video/3537342483001'
    video = zeit.cms.interfaces.ICMSContent(unique_id)
    group = zeit.content.image.interfaces.IImageGroup(video)
    image = group[img]
    assert image.getImageSize() == res
