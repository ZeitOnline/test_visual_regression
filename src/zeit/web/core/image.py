import datetime
import hashlib
import logging
import os
import re
import tempfile

import PIL
import pytz
import requests
import requests_file
import grokcore.component
import zc.sourcefactory.contextual
import zc.sourcefactory.source
import zope.component

import zeit.cms.workflow.interfaces
import zeit.content.image.imagegroup
import zeit.content.image.interfaces
import zeit.content.image.variant

import zeit.web
import zeit.web.core.cache
import zeit.web.core.metrics


log = logging.getLogger(__name__)
CONFIG_CACHE = zeit.web.core.cache.get_region('config')


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

        self.group = zeit.content.image.interfaces.IImageGroup(variant)
        self.image_group = self.group.uniqueId
        self.path = self.group.variant_url(
            self.image_pattern,
            # XXX Slightly kludgy: fill_color is not a property of Variant but
            # only transported through there by z.w.core.template.get_variant.
            fill_color=getattr(variant, 'fill_color', None))
        self.fallback_path = self.group.variant_url(
            self.image_pattern,
            variant.fallback_width,
            variant.fallback_height)

        meta = zeit.content.image.interfaces.IImageMetadata(self.group, None)
        if meta:
            self.alt = meta.alt
            self.caption = meta.caption
            self.copyright = meta.copyrights
            self.title = meta.title


class LocalImage(object):

    KiB = 1024
    DOWNLOAD_CHUNK_SIZE = 2 * KiB

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
        # XXX requests does not seem to allow to mount stuff as a default, sigh
        session = requests.Session()
        session.mount('file://', requests_file.FileAdapter())
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        try:
            with zeit.web.core.metrics.timer(
                    'zeit.web.core.video.thumbnail.brightcove.response_time'):
                response = session.get(
                    self.url, stream=True,
                    timeout=conf.get('brightcove_image_timeout', 2))
                response.raise_for_status()
            with self.open(mode='w+') as fh:
                first_chunk = True
                for chunk in response.iter_content(self.DOWNLOAD_CHUNK_SIZE):
                    # Too small means something is not right with this download
                    if first_chunk:
                        first_chunk = False
                        assert len(chunk) > self.DOWNLOAD_CHUNK_SIZE / 2
                    fh.write(chunk)
            # Analoguous to requests.api.request().
            session.close()
        except (requests.exceptions.RequestException, IOError, AssertionError):
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
        try:
            image = LocalImage(self.image_url)
        except TypeError:
            return None
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
    elif isinstance(image, VariantImage):
        group = image.group
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


class ScaleSource(zeit.imp.source.ScaleSource):

    def isAvailable(self, *args):  # NOQA
        # Contrary to CMS behavior, we do not want to hide any image scales
        # in zeit.web, so availability is `True` regardless of context.
        return True

SCALE_SOURCE = ScaleSource()(None)


class ImageScales(zc.sourcefactory.contextual.BasicContextualSourceFactory):
    # Only contextual so we can customize source_class

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        def find(self, id):
            return self.factory.getValues(None).get(id)

    def getValues(self, context):
        def sub(x):
            return int(re.sub('[^0-9]', '', '0' + str(x)))

        return {s.name: (sub(s.width), sub(s.height)) for s in SCALE_SOURCE}

IMAGE_SCALE_SOURCE = ImageScales()(None)


class VariantSource(zeit.content.image.variant.VariantSource):

    product_configuration = 'zeit.content.image'
    config_url = 'variant-source'

    def find(self, context, variant_id):
        mapping = self._get_mapping()
        tree = self._get_tree()
        for node in tree.iterchildren('*'):
            if not self.isAvailable(node, context):
                continue

            attributes = dict(node.attrib)
            mapped = mapping.get(variant_id, variant_id)

            if attributes['name'] == mapped:
                attributes['id'] = attributes['name']
                variant = zeit.content.image.variant.Variant(**attributes)
                if variant_id != mapped:
                    variant.legacy_name = variant_id
                return variant
        raise KeyError(variant_id)

    @CONFIG_CACHE.cache_on_arguments()
    def _get_mapping(self):
        return {k['old']: k['new'] for k in
                zeit.content.image.variant.LEGACY_VARIANT_SOURCE(None)}


VARIANT_SOURCE = VariantSource()
