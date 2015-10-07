import hashlib
import logging
import os
import PIL
import tempfile
import urllib2

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
import zeit.web.site.area.spektrum


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
            self.path = group.variant_url(self.image_pattern)
            self.fallback_path = group.variant_url(
                self.image_pattern,
                variant.fallback_width,
                variant.fallback_height)
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


class LocalImage(object):

    def __init__(self, url):
        self.url = url
        self.mimeType = 'image/jpeg'
        self.format = 'jpeg'
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        tempdir = conf.get('brightcove_image_cache', tempfile.gettempdir())
        hashkey = hashlib.md5(self.url.encode('ascii', errors='ignore'))
        self.__name__ = '{}/{}'.format(tempdir, hashkey.hexdigest())
        self.fetch()

    def isfile(self):
        return os.path.isfile(self.__name__)

    def fetch(self):
        if self.isfile():
            return
        try:
            # XXX: Switch to requests to leverage urllib3 connection pooling.
            resp = urllib2.urlopen(self.url, timeout=2)
            content = resp.read()
            assert len(content) > 1024
            with self.open(mode='w+') as fh:
                fh.write(content)
        except (AssertionError, IOError, ValueError):
            log.debug('Remote image {} could not be downloaded to {}.'.format(
                      self.url, self.__name__))
            raise TypeError('Could not adapt {}'.format(self.url))

    def open(self, mode='r'):
        return open(self.__name__, mode)

    @zeit.web.reify
    def size(self):
        if self.isfile():
            return os.stat(self.__name__).st_size
        return 0

    def getImageSize(self):  # NOQA
        if self.isfile():
            with self.open() as fh:
                return PIL.Image.open(fh).size
        return (0, 0)


class LocalImageGroup(zeit.content.image.imagegroup.ImageGroup,
                      zeit.web.core.utils.nsdict):

    def __init__(self, context):
        super(LocalImageGroup, self).__init__()
        self.context = context

    def __getitem__(self, key):
        return self.create_variant_image(key)

    def __repr__(self):
        return object.__repr__(self)

    def __len__(self):
        return int(bool(self.master_image))

    def __contains__(self, key):
        # Local image groups *only* contain master images.
        return False

    def keys(self):
        # Local image groups *only* contain master images.
        return ()

    @property
    def master_image(self):
        return self._master_image

    @master_image.setter
    def master_image(self, value):
        self._master_image = value


@grokcore.component.implementer(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.adapter(zeit.content.video.interfaces.IVideo)
class VideoImageGroup(LocalImageGroup):

    def __init__(self, context):
        super(VideoImageGroup, self).__init__(context)
        self.uniqueId = '{}/imagegroup/'.format(context.uniqueId)
        self.master_image = image = LocalImage(context.video_still)

        self.copyrights = (context.copyrights or '').strip('\n')
        self.teaserText = (context.teaserText or '').strip('\n')
        self.teaserTitle = (context.teaserTitle or '').strip('\n')
        self.title = (context.title or '').strip('\n')

        image.src = context.video_still
        image.mimeType = 'image/jpeg'
        image.image_pattern = 'widelarge'
        image.copyright = self.copyrights
        image.caption = self.teaserText
        image.title = self.teaserTitle
        image.alt = self.title
        image.uniqueId = '{}still.jpg'.format(self.uniqueId)


# VideoImageGroup = ImageGroup  # XXX This should move out of centerpage.py

@grokcore.component.implementer(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.adapter(zeit.web.site.area.spektrum.Teaser)
class SpektrumImageGroup(LocalImageGroup):

    def __init__(self, context):
        super(SpektrumImageGroup, self).__init__(context)
        self.master_image = image = LocalImage(context.image_url)
        self.uniqueId = 'http://xml.zeit.de/spektrum-image{}'.format(
            context.image_url.replace('http://www.spektrum.de', ''))

        self.copyrights = (context.copyrights or '').strip('\n')
        self.teaserText = (context.teaserText or '').strip('\n')
        self.teaserTitle = (context.teaserTitle or '').strip('\n')
        self.title = (context.title or '').strip('\n')

        image.src = context.image_url
        image.mimeType = 'image/jpeg'
        image.image_pattern = 'widelarge'
        image.copyright = self.copyrights
        image.caption = self.teaserText
        image.title = self.teaserTitle
        image.alt = self.title
        image.uniqueId = '{}/wide'.format(self.uniqueId)


@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
@grokcore.component.adapter(zeit.content.video.interfaces.IVideo)
class VideoImages(object):

    def __init__(self, context):
        self.context = context
        self.image = zeit.content.image.interfaces.IImageGroup(context)


@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
@grokcore.component.adapter(zeit.web.site.area.spektrum.Teaser)
class SpektrumImages(object):

    def __init__(self, context):
        # XXX combine with VideoImages?
        self.context = context
        self.image = zeit.content.image.interfaces.IImageGroup(context)


@grokcore.component.implementer(zeit.content.image.interfaces.IImageMetadata)
@grokcore.component.adapter(LocalImageGroup)
class LocalImageMetaData(object):

    def __init__(self, group):
        for field in zeit.content.image.interfaces.IImageMetadata:
            setattr(self, field, None)
        self.alt = group.title
        self.caption = group.teaserText
        self.title = group.teaserTitle
        self.copyrights = group.copyrights


@grokcore.component.implementer(zeit.content.image.interfaces.IMasterImage)
@grokcore.component.adapter(LocalImageGroup)
def localimagegroup_to_masterimage(group):
    return group.master_image


@grokcore.component.implementer(
    zeit.content.image.interfaces.IRepositoryImageGroup)
@grokcore.component.adapter(LocalImageGroup)
def localimagegroup_to_repositoryimagegroup(group):
    return group


@grokcore.component.implementer(zeit.content.image.interfaces.ITransform)
@grokcore.component.adapter(LocalImage)
def localimage_to_imagetransform(image):
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
