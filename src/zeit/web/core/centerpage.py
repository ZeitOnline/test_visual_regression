import logging
import urllib2
import md5
import tempfile
import PIL
import os

import grokcore.component
import zope.component

import zeit.cms.interfaces
import zeit.content.cp.interfaces
import zeit.content.gallery.interfaces
import zeit.content.image.imagegroup
import zeit.content.image.interfaces
import zeit.content.video.interfaces
import zeit.content.image.image

import zeit.web
import zeit.web.core.block
import zeit.web.core.interfaces
import zeit.web.core.utils
import zeit.web.site.area.spektrum


log = logging.getLogger(__name__)


@zeit.web.register_filter
def get_all_assets(teaser):
    try:
        assets = (get_video_asset(teaser),
                  get_gallery_asset(teaser),
                  get_image_asset(teaser))
        return tuple(a for a in assets if a)
    except TypeError:
        log.debug('No assets for %s' % teaser.uniqueId)
        return ()


@zeit.web.register_filter
def auto_select_asset(teaser):
    assets = get_all_assets(teaser)
    if len(assets):
        return assets[0]


def get_video_asset(teaser):

    def get_video_source(self):
        try:
            highest_rendition = self.renditions[0]
            for rendition in self.renditions:
                if highest_rendition.frame_width < rendition.frame_width:
                    highest_rendition = rendition
            return highest_rendition.url
        except (AttributeError, IndexError, TypeError):
            return self.flv_url

    try:
        asset = zeit.content.video.interfaces.IVideoAsset(teaser)
    except TypeError:
        return

    if asset.video is not None:
        asset.video.highest_rendition = get_video_source(asset.video)

    if asset.video_2 is not None and asset.video is not None:
        asset.video_2.highest_rendition = get_video_source(asset.video_2)
        return [asset.video, asset.video_2]

    return asset.video


def get_gallery_asset(teaser):
    try:
        return zeit.content.gallery.interfaces.IGalleryReference(
            teaser).gallery
    except (TypeError, AttributeError):
        return


@zeit.web.register_filter
def get_image_asset(teaser):
    try:
        return zeit.content.image.interfaces.IImages(teaser).image
    except (TypeError, AttributeError):
        return


class TeaserSequence(object):

    def __init__(self, context):
        self.context = context
        self.sequence = []
        self.refs = []

    def __contains__(self, item):
        return item in self.sequence

    def __iter__(self):
        return iter(self.sequence)

    def __len__(self):
        return len(self.sequence)

    def __setitem__(self, key, value):
        index = self.sequence.index(key)
        self.refs[index][key] = value

    def __getitem__(self, key):
        return self.sequence[key]

    def __delitem__(self, key):
        del self.sequence[key]

    def __repr__(self):
        return object.__repr__(self)

    def _resolve_child(self, item):
        try:
            sub_seq = zeit.web.core.interfaces.ITeaserSequence(item)
            self.sequence += sub_seq.sequence
            self.refs += sub_seq.refs
            return
        except TypeError:
            pass
        try:
            self.sequence.append(zeit.web.core.centerpage.Teaser(
                self.context, item))
            self.refs.append(self.context)
        except TypeError:
            pass


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserSequence)
@grokcore.component.adapter(list)
class TeaserList(TeaserSequence):

    def __init__(self, context):
        super(TeaserList, self).__init__(context)
        for item in iter(context):
            self._resolve_child(item)


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserSequence)
@grokcore.component.adapter(zeit.content.cp.interfaces.ITeaserBlock)
class TeaserBlock(TeaserList):

    pass


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserSequence)
@grokcore.component.adapter(dict)
class TeaserDict(TeaserSequence):

    def __init__(self, context):
        super(TeaserDict, self).__init__(context)
        for item in context.itervalues():
            self._resolve_child(item)


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserSequence)
@grokcore.component.adapter(zeit.content.cp.interfaces.IArea)
class Area(TeaserDict):

    pass


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaser)
@grokcore.component.adapter(TeaserSequence, zeit.cms.interfaces.ICMSContent)
class Teaser(object):

    def __init__(self, block, context):
        self.video = None
        self.gallery = None
        self.image = zeit.web.core.template.get_teaser_image(block, context)
        self.context = context


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserImage)
@grokcore.component.adapter(zeit.content.image.interfaces.IImage)
class Image(zeit.web.core.block.BaseImage):

    def __init__(self, image):
        meta = zeit.content.image.interfaces.IImageMetadata(image)
        self.align = None
        self.alt = meta.alt
        self.attr_alt = meta.alt or meta.caption
        self.attr_title = meta.title or meta.caption
        self.caption = meta.caption
        self.copyright = meta.copyrights
        self.image = image
        self.image_group = None
        self.image_pattern = 'default'
        self.layout = ''
        self.src = self.uniqueId = image.uniqueId
        self.title = meta.title


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserImage)
@grokcore.component.adapter(zeit.content.image.interfaces.IImageGroup,
                            zeit.content.image.interfaces.IImage)
class TeaserImage(zeit.web.core.block.BaseImage):

    def __init__(self, image_group, image):
        meta = zeit.content.image.interfaces.IImageMetadata(image_group)
        self.align = None
        self.alt = meta.alt
        self.attr_alt = meta.alt or meta.caption
        self.attr_title = meta.title or meta.caption
        self.caption = meta.caption
        self.copyright = meta.copyrights
        self.image = image
        self.image_group = image_group.uniqueId
        self.image_pattern = 'default'
        self.layout = ''
        self.src = self.uniqueId = image.uniqueId
        self.title = meta.title
        self.uniqueId = image.uniqueId


class LocalVideoImage(object):

    def __init__(self, video_url):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        self.filename = "{}/{}".format(
            conf.get('brightcove_image_cache', tempfile.gettempdir()),
            md5.new(video_url).hexdigest())

    def open(self, mode="r"):
        return open(self.filename, mode)

    def isfile(self):
        return os.path.isfile(self.filename)

    @zeit.web.reify
    def size(self):
        if self.isfile():
            return os.stat(self.filename).st_size
        return 0

    def getImageSize(self):  # NOQA
        if self.isfile():
            return PIL.Image.open(self.open()).size
        return (0, 0)


class ContentTooShort(Exception):
    pass


@grokcore.component.implementer(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.adapter(zeit.content.video.interfaces.IVideo)
class VideoImageGroup(zeit.content.image.imagegroup.ImageGroupBase,
                      zeit.web.core.utils.nsdict):

    master_image = None

    def __init__(self, video):
        super(VideoImageGroup, self).__init__()
        self.uniqueId = '{}/imagegroup/'.format(video.uniqueId)
        return
        for image_pattern, src in [('still', video.video_still),
                                   ('thumbnail', video.thumbnail)]:
            image = zeit.web.core.block.BaseImage()

            image.image = LocalVideoImage(src)
            file_name = '{}.jpg'.format(image_pattern)

            if not image.image.isfile():
                try:
                    request = urllib2.urlopen(src, timeout=1.5)
                    content = request.read()
                    if len(content) <= 20:
                        raise ContentTooShort()

                    with image.image.open('w+') as fh:
                        fh.write(content)
                        log.debug("Save brightcove image {} "
                                  "to local file {}".format(
                                      src,
                                      image.image.filename))
                except (IOError, AttributeError, ContentTooShort):
                    try:
                        conf = zope.component.getUtility(
                            zeit.web.core.interfaces.ISettings)

                        image.image = zeit.cms.interfaces.ICMSContent(
                            '{}/{}'.format(
                                conf.get('default_teaser_images'),
                                'teaser_image-default.jpg'))
                    except:
                        continue
            image.src = src
            image.mimeType = 'image/jpeg'
            image.image_pattern = 'brightcove-{}'.format(image_pattern)
            image.copyright = video.copyrights
            image.caption = (video.teaserText or '').strip('\n')
            image.title = (video.teaserTitle or '').strip('\n')
            image.alt = (video.title or '').strip('\n')
            image.uniqueId = '{}{}'.format(self.uniqueId, file_name)
            self[file_name] = image

    def __repr__(self):
        return object.__repr__(self)


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserImage)
@grokcore.component.adapter(zeit.web.site.area.spektrum.Teaser)
class SpektrumImage(zeit.web.core.block.BaseImage):

    def __init__(self, context):
        super(SpektrumImage, self).__init__()

        if context.feed_image is None:
            raise TypeError('Could not adpat', context,
                            zeit.web.core.interfaces.ITeaserImage)

        self.image = zeit.content.image.image.LocalImage()

        try:
            with self.image.open('w') as fh:
                fileobj = urllib2.urlopen(context.feed_image, timeout=4)
                fh.write(fileobj.read())
        except IOError:
            raise TypeError('Image was not found on spektrum server.')

        self.mimeType = fileobj.headers.get('Content-Type')
        self.image_pattern = 'spektrum'
        self.caption = context.teaserText
        self.title = context.teaserTitle
        self.alt = context.teaserTitle
        self.uniqueId = 'http://xml.zeit.de/spektrum-image{}'.format(
            context.feed_image.replace('http://www.spektrum.de', ''))


@grokcore.component.implementer(zeit.web.core.interfaces.ITopicLink)
@grokcore.component.adapter(zeit.content.cp.interfaces.ICenterPage)
class TopicLink(zeit.web.core.utils.nslist):
    """Filter and restructure all topiclinks and labels
    :rtype: generator
    """

    def __init__(self, context):
        self.context = context
        self.title = context.topiclink_title or 'Schwerpunkte'
        for i in xrange(1, 4):
            label = getattr(self.context, 'topiclink_label_%s' % i, None)
            link = getattr(self.context, 'topiclink_url_%s' % i, None)
            if label is not None and link is not None:
                self.append((label, link))
