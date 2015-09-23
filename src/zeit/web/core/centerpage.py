import logging
import urllib2
import md5
import tempfile
import PIL
import os

import grokcore.component
import zope.component

import zeit.cms.interfaces
import zeit.content.cp.area
import zeit.content.cp.interfaces
import zeit.content.gallery.interfaces
import zeit.content.image.imagegroup
import zeit.content.image.interfaces
import zeit.content.video.interfaces

import zeit.web
import zeit.web.core.block
import zeit.web.core.interfaces
import zeit.web.core.utils


log = logging.getLogger(__name__)


@zeit.web.register_filter
def auto_select_asset(teaser):
    for getter in (get_video_asset, get_gallery_asset, get_image_asset):
        asset = getter(teaser)
        if asset:
            return asset
    log.debug('No assets for %s' % teaser.uniqueId)


@zeit.web.register_filter
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


@zeit.web.register_filter
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


def get_area(area):
    return zeit.web.core.utils.get_named_adapter(
        area, zeit.content.cp.interfaces.IRenderedArea, 'kind')


class IRendered(zope.interface.Interface):
    """Calculates values() only once.
    """


@grokcore.component.adapter(zeit.content.cp.interfaces.IRegion)
@grokcore.component.implementer(IRendered)
class RenderedRegion(zeit.content.cp.area.Region):

    def __init__(self, context):
        super(RenderedRegion, self).__init__(context.__parent__, context.xml)

    def values(self):
        if not hasattr(self, '_v_values'):
            self._v_values = [IRendered(get_area(x))
                              for x in super(RenderedRegion, self).values()]
        return self._v_values


@grokcore.component.adapter(zeit.content.cp.interfaces.IArea)
@grokcore.component.implementer(IRendered)
def cache_values_area(context):
    def cached_values(self):
        return self._v_values
    context._v_values = context.values()
    context.values = cached_values.__get__(context)
    return context


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
        self.align = None
        self.image = image
        self.image_pattern = 'default'
        self.layout = ''
        self.src = self.uniqueId = image.uniqueId

        group = zeit.content.image.interfaces.IImageGroup(image, None)
        if group:
            self.image_group = group.uniqueId
        else:
            self.image_group = None

        meta = zeit.content.image.interfaces.IImageMetadata(image, None)
        if meta:
            self.alt = meta.alt
            self.attr_alt = meta.alt or meta.caption
            self.attr_title = meta.title or meta.caption
            self.caption = meta.caption
            self.copyright = meta.copyrights
            self.title = meta.title


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserImage)
@grokcore.component.adapter(zeit.content.image.interfaces.IImageGroup,
                            zeit.content.image.interfaces.IImage)
class TeaserImage(zeit.web.core.block.BaseImage):

    def __init__(self, group, image):
        self.align = None
        self.image = image
        self.image_group = group.uniqueId
        self.image_pattern = 'default'
        self.layout = ''
        self.src = self.uniqueId = image.uniqueId
        self.uniqueId = image.uniqueId

        meta = zeit.content.image.interfaces.IImageMetadata(group, None)
        if meta:
            self.alt = meta.alt
            self.attr_alt = meta.alt or meta.caption
            self.attr_title = meta.title or meta.caption
            self.caption = meta.caption
            self.copyright = meta.copyrights
            self.title = meta.title


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserImage)
@grokcore.component.adapter(zeit.content.image.interfaces.IVariant)
class VariantImage(object):

    def __init__(self, variant):
        self.image_pattern = variant.name
        self.ratio = variant.ratio
        self.variant = variant.legacy_name or variant.name

        group = zeit.content.image.interfaces.IImageGroup(variant, None)
        if group:
            self.image_group = group.uniqueId
            self.path = group.variant_url(self.image_pattern).lstrip('/')
            self.fallback_path = group.variant_url(
                self.image_pattern,
                variant.fallback_width,
                variant.fallback_height).lstrip('/')
        else:
            self.image_group = None

        meta = zeit.content.image.interfaces.IImageMetadata(group, None)
        if meta:
            self.alt = meta.alt
            self.attr_alt = meta.alt or meta.caption
            self.attr_title = meta.title or meta.caption
            self.caption = meta.caption
            self.copyright = meta.copyrights
            self.title = meta.title


class LocalVideoImage(object):

    def __new__(cls, video_url, video_id):
        instance = object.__new__(cls)
        instance.__init__(video_url, video_id)
        try:
            instance.fetch()
        except VideoImageNotFound:
            return cls.fallback_image()
        return instance

    def __init__(self, video_url, video_id):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        self.url = video_url or ''
        self.video_id = video_id
        self.mimeType = 'image/jpeg'
        self.format = 'jpeg'
        self.__name__ = '{}/{}'.format(
            conf.get('brightcove_image_cache', tempfile.gettempdir()),
            md5.new(self.url).hexdigest())

    def isfile(self):
        return os.path.isfile(self.__name__)

    def fetch(self):
        if self.isfile():
            return
        if not self.url:
            # Even though video_still and thumbnail should always be set,
            # especially in some older videos they are empty for unknown
            # reasons.
            raise VideoImageNotFound()
        try:
            resp = urllib2.urlopen(self.url, timeout=1.5)
            content = resp.read()
            if len(content) <= 20:
                raise ContentTooShort()

            with self.open('w+') as fh:
                fh.write(content)
                log.debug(
                    'Save brightcove image {} for {} to local file {}'.format(
                        self.url, self.video_id, self.__name__))
        except (IOError, AttributeError, ContentTooShort):
            raise VideoImageNotFound()

    @classmethod
    def fallback_image(cls):
        try:
            conf = zope.component.getUtility(
                zeit.web.core.interfaces.ISettings)
            return zeit.cms.interfaces.ICMSContent(
                '{}/{}'.format(
                    conf.get('default_teaser_images'),
                    'teaser_image-default.jpg'))
        except:
            raise VideoImageNotFound()

    def open(self, mode='r'):
        return open(self.__name__, mode)

    @zeit.web.reify
    def size(self):
        if self.isfile():
            return os.stat(self.__name__).st_size
        return 0

    def getImageSize(self):  # NOQA
        if self.isfile():
            return PIL.Image.open(self.open()).size
        return (0, 0)


class ContentTooShort(Exception):
    pass


class VideoImageNotFound(Exception):
    pass


@grokcore.component.implementer(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.adapter(zeit.content.video.interfaces.IVideo)
class ImageGroup(zeit.content.image.imagegroup.ImageGroup,
                 zeit.web.core.utils.nsdict):

    def __init__(self, video):
        super(ImageGroup, self).__init__()
        self.uniqueId = '{}/imagegroup/'.format(video.uniqueId)
        self.copyrights = copyrights = (video.copyrights or '').strip('\n')
        self.teaserText = teaserText = (video.teaserText or '').strip('\n')
        self.teaserTitle = teaserTitle = (video.teaserTitle or '').strip('\n')
        self.title = title = (video.title or '').strip('\n')
        try:
            image = LocalVideoImage(video.video_still, video.uniqueId)
        except VideoImageNotFound:
            image = None
        else:
            image.src = video.video_still
            image.mimeType = 'image/jpeg'
            image.image_pattern = 'wide-large'
            image.copyright = copyrights
            image.caption = teaserText
            image.title = teaserTitle
            image.alt = title
            image.uniqueId = '{}{}'.format(self.uniqueId, 'still.jpg')
        self.master_image = image

    def __getitem__(self, key):
        return self.create_variant_image(key)

    def __repr__(self):
        return object.__repr__(self)

    def __len__(self):
        return int(bool(self.master_image))

    def __contains__(self, key):
        return False  # Video imagegroups *only* contain master images.

    def keys(self):
        return ()  # Video imagegroups *only* contain master images.

    @property
    def master_image(self):
        return self._master_image

    @master_image.setter
    def master_image(self, value):
        self._master_image = value


VideoImageGroup = ImageGroup  # XXX This should move out of centerpage.py


@grokcore.component.implementer(
    zeit.content.image.interfaces.IRepositoryImageGroup)
@grokcore.component.adapter(VideoImageGroup)
def videoimagegroup_to_repositoryimagegroup(group):
    return group


@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
@grokcore.component.adapter(zeit.content.video.interfaces.IVideo)
class VideoImages(object):

    def __init__(self, video):
        self.context = video
        self.image = zeit.content.image.interfaces.IImageGroup(video)


@grokcore.component.implementer(zeit.content.image.interfaces.IImageMetadata)
@grokcore.component.adapter(VideoImageGroup)
class VideoImageMetaData(object):

    def __init__(self, group):
        for field in zeit.content.image.interfaces.IImageMetadata:
            setattr(self, field, None)
        self.alt = group.title
        self.caption = group.teaserText
        self.title = group.teaserTitle
        self.copyrights = group.copyrights


@grokcore.component.implementer(zeit.content.image.interfaces.IMasterImage)
@grokcore.component.adapter(VideoImageGroup)
def videoimagegroup_to_masterimage(group):
    return group.master_image


@grokcore.component.implementer(zeit.content.image.interfaces.ITransform)
@grokcore.component.adapter(LocalVideoImage)
def videoimage_to_imagetransform(image):
    return zeit.content.image.transform.ImageTransform(image)


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


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserSequence)
@grokcore.component.adapter(zeit.web.core.interfaces.INextread)
class Nextread(TeaserBlock):
    pass
