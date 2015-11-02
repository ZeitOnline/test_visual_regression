import datetime
import hashlib
import logging
import os
import PIL
import tempfile
import urllib2

import pytz
import grokcore.component
import zope.component

import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.cp.area
import zeit.content.cp.interfaces
import zeit.content.gallery.interfaces
import zeit.content.image.imagegroup
import zeit.content.image.interfaces
import zeit.content.video.interfaces

import zeit.web
import zeit.web.core.metrics


log = logging.getLogger(__name__)


class BaseImage(object):

    @property
    def ratio(self):
        try:
            width, height = self.image.getImageSize()
            return float(width) / float(height)
        except (TypeError, ZeroDivisionError):
            return

    def getImageSize(self):  # NOQA
        try:
            return self.image.getImageSize()
        except AttributeError:
            return


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserImage)
@grokcore.component.adapter(zeit.content.image.interfaces.IImage)
class Image(BaseImage):

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
            self.caption = meta.caption
            self.copyright = meta.copyrights
            self.title = meta.title


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserImage)
@grokcore.component.adapter(zeit.content.image.interfaces.IImageGroup,
                            zeit.content.image.interfaces.IImage)
class TeaserImage(BaseImage):

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

        group = zeit.content.image.interfaces.IImageGroup(variant)
        self.image_group = group.uniqueId
        self.path = group.variant_url(self.image_pattern)
        self.fallback_path = group.variant_url(
            self.image_pattern,
            variant.fallback_width,
            variant.fallback_height)

        meta = zeit.content.image.interfaces.IImageMetadata(group, None)
        if meta:
            self.alt = meta.alt
            self.caption = meta.caption
            self.copyright = meta.copyrights
            self.title = meta.title


class LocalImage(object):

    def __init__(self, url):
        if not isinstance(url, basestring):
            raise TypeError('Local image URL needs to be string formatted')
        self.url = url
        self.mimeType = 'image/jpeg'
        self.format = 'jpeg'
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        tempdir = conf.get('brightcove_image_cache', tempfile.gettempdir())
        hashkey = hashlib.md5(self.url.encode('ascii', errors='replace'))
        self.__name__ = '{}/{}'.format(tempdir, hashkey.hexdigest())
        self.fetch()

    def isfile(self):
        return os.path.isfile(self.__name__)

    def fetch(self):
        if self.isfile():
            return
        try:
            # TODO: Switch to requests to leverage urllib3 connection pooling.
            with zeit.web.core.metrics.timer(
                    'zeit.web.core.video.thumbnail.brightcove.response_time'):
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

    @zeit.web.reify
    def copyrights(self):
        return (getattr(self.context, 'copyrights', None) or '').strip()

    @zeit.web.reify
    def teaserText(self):  # NOQA
        return (getattr(self.context, 'teaserText', None) or '').strip()

    @zeit.web.reify
    def teaserTitle(self):  # NOQA
        return (getattr(self.context, 'teaserTitle', None) or '').strip()

    @zeit.web.reify
    def title(self):
        return (getattr(self.context, 'title', None) or '').strip()

    @zeit.web.reify
    def master_image(self):
        image = LocalImage(self.image_url)
        image.src = self.image_url
        image.mimeType = 'image/jpeg'
        image.image_pattern = 'wide-large'
        image.copyright = self.copyrights
        image.caption = self.teaserText
        image.title = self.teaserTitle
        image.alt = self.title
        return image


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


@grokcore.component.implementer(zeit.content.image.interfaces.ITransform)
@grokcore.component.adapter(LocalImage)
def localimage_to_imagetransform(image):
    return zeit.content.image.transform.ImageTransform(image)


# XXX Should this be a method of Image/ImageGroup?
def image_expires(image):
    """Returns number of seconds relative to now when the given image, or the
    image group it belongs to, will no longer be published.
    """
    if zeit.content.image.interfaces.IImage.providedBy(image):
        group = image.__parent__
    else:
        group = image
    if not zeit.content.image.interfaces.IImageGroup.providedBy(group):
        return None

    workflow = zeit.cms.workflow.interfaces.IPublishInfo(group)
    if workflow.released_to:
        now = datetime.datetime.now(pytz.UTC)
        return int((workflow.released_to - now).total_seconds())


@zeit.web.register_global
def is_image_expired(image):
    expires = image_expires(image)
    if expires is None:
        return False
    return (expires < 0)
