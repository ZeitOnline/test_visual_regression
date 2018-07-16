# coding: utf-8
import datetime
import hashlib
import logging
import os
import tempfile
import urllib

import PIL
import pkg_resources
import pytz
import requests
import requests_file
import grokcore.component
import zope.component
import zope.interface

from zeit.cms.checkout.interfaces import ILocalContent
import zeit.cms.workflow.interfaces
import zeit.content.author.interfaces
import zeit.content.gallery.interfaces
import zeit.content.image.imagegroup
import zeit.content.image.imagereference
import zeit.content.image.interfaces
import zeit.content.image.variant

import zeit.web
import zeit.web.core.cache
import zeit.web.core.block
import zeit.web.core.metrics
import zeit.web.core.template


log = logging.getLogger(__name__)
CONFIG_CACHE = zeit.web.core.cache.get_region('config')


class Image(object):
    """Base class for all template-bound images in friedbert"""

    grokcore.component.implements(zeit.web.core.interfaces.IImage)

    def __init__(self, context):
        self.context = context

    def __bool__(self):
        # Images shall evaluate to false if they don't actually have images
        return bool(self.group)

    __nonzero__ = __bool__

    def __repr__(self):
        return '<%s.%s %s>' % (
            self.__class__.__module__, self.__class__.__name__,
            self.group)

    @zeit.web.reify
    def _meta(self):
        # Image metadata is retrieved from the underlying group by default
        # but this can be overwritten to include block metadata for example
        return zeit.content.image.interfaces.IImageMetadata(self.group, None)

    @zeit.web.reify
    def _images(self):
        # The CMS mechanics for extracting a single image or an image group
        # from a piece of content (or fragment of it, ie teaserblock)
        # is applied here but can be overwritten if necessary
        return zeit.content.image.interfaces.IImages(self.context, None)

    @zeit.web.reify
    def _variant(self):
        # Override hook for variant object retrieval
        try:
            variant = VARIANT_SOURCE.factory.find(
                self.group, self.variant_id)
        except KeyError:
            variant = VARIANT_SOURCE.factory.find(self.group)
        variant.__parent__ = self.group
        return variant

    @zeit.web.reify
    def group(self):
        # Contains a valid (synthesized) imagegroup
        if hasattr(self._images, 'image'):
            return zeit.content.image.interfaces.IImageGroup(
                self._images.image, None)

    @zeit.web.reify
    def copyrights(self):
        copyrights = []
        if self._meta and self._meta.copyrights:
            for item in self._meta.copyrights:
                photographer, company, company_text, url, nf = item
                text = photographer or ''
                text = zeit.web.core.utils.fix_misrepresented_latin(
                    text).replace(u'© ', u'© ').strip()
                if text == u'©':
                    continue
                if company_text:
                    company = company_text
                if company:
                    text += u'/' + company
                copyrights.append({
                    'text': text,
                    'photographer': photographer,
                    'company': company,
                    'external_id': self._meta.external_id,
                    'url': url,
                    'nofollow': nf,
                })
        return tuple(copyrights)

    @zeit.web.reify
    def title(self):
        if self._meta:
            return self._meta.title

    @zeit.web.reify
    def alt(self):
        if self._meta:
            return self._meta.alt

    @zeit.web.reify
    def caption(self):
        if self._meta:
            return self._meta.caption

    @zeit.web.reify
    def href(self):
        if self._meta:
            return self._meta.links_to

    @zeit.web.reify
    def nofollow(self):
        if self._meta:
            return self._meta.nofollow

    @zeit.web.reify
    def origin(self):
        if self._meta:
            return self._meta.origin

    @zeit.web.reify
    def fill_color(self):
        if hasattr(self._images, 'fill_color'):
            return self._images.fill_color

    @zeit.web.reify
    def variant_id(self):
        # This should actually be called variant_name, but raisins (ND)
        return VARIANT_SOURCE.factory.DEFAULT_NAME

    def _ratio_for_viewport(self, viewport):
        # If the variant config does not provide a ratio, we try to determine
        # it from the viewport-specific masterimage
        if zeit.content.image.interfaces.IImageGroup.providedBy(self.group):
            image = self.group.master_image_for_viewport(viewport)
            if image is None:
                return
            width, height = image.getImageSize()
            return float(width) / float(height)

    @zeit.web.reify
    def ratio(self):
        if self._variant.ratio is None:
            return self._ratio_for_viewport('desktop')
        else:
            return self._variant.ratio

    @zeit.web.reify
    def mobile_ratio(self):
        if self._variant.ratio is None:
            mobile = self._ratio_for_viewport('mobile')
            if mobile and self.ratio and round(abs(mobile - self.ratio), 3):
                return mobile

    @zeit.web.reify
    def fallback_width(self):
        return self._variant.fallback_width

    @zeit.web.reify
    def fallback_height(self):
        return self._variant.fallback_height

    @zeit.web.reify
    def path(self):
        url = self.group.variant_url(
            self.variant_id,
            fill_color=self.fill_color)
        return urllib.quote(url.encode('utf-8'))

    @zeit.web.reify
    def fallback_path(self):
        url = self.group.variant_url(
            self.variant_id,
            width=self.fallback_width,
            height=self.fallback_height,
            fill_color=self.fill_color)
        return urllib.quote(url.encode('utf-8'))


@grokcore.component.adapter(zeit.cms.interfaces.ICMSContent)
@grokcore.component.implementer(zeit.web.core.interfaces.IImage)
class CMSContentImage(Image):
    """Default image for all top-level content types.
    They usually have no way of knowing their variant and fallback to the
    original. Deviations should be set in templates."""

    pass


@grokcore.component.adapter(zeit.web.core.interfaces.IBlock)
@grokcore.component.implementer(zeit.web.core.interfaces.IImage)
class ModuleImage(Image):
    """Image adapter for friedbert specific zeit.edit block implementations"""

    @zeit.web.reify
    def variant_id(self):
        if self.context.layout.image_pattern:
            return self.context.layout.image_pattern
        else:
            return super(ModuleImage, self).variant_id


@grokcore.component.adapter(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.implementer(zeit.web.core.interfaces.IImage)
class ImageGroupImage(Image):

    @zeit.web.reify
    def group(self):
        return self.context


@grokcore.component.adapter(zeit.content.image.interfaces.IImage)
@grokcore.component.implementer(zeit.web.core.interfaces.IImage)
class SingleImageImage(Image):

    @zeit.web.reify
    def group(self):
        return zeit.content.image.interfaces.IImageGroup(self.context, None)


@grokcore.component.adapter(zeit.content.gallery.interfaces.IGallery,
                            name=u'content')
@grokcore.component.implementer(zeit.web.core.interfaces.IImage)
def image_for_gallery(context):
    """Content adapter for gallery images, that extracts the image from the
    first slide of a gallery. Popular example would be the HP snapshot"""

    for key in context.keys():
        try:
            entry = context[key]
        except:
            continue
        else:
            if zeit.web.core.template.hidden_slide(entry):
                continue
            return zeit.web.core.interfaces.IImage(entry)


@grokcore.component.adapter(zeit.content.gallery.interfaces.IGalleryEntry)
@grokcore.component.implementer(zeit.web.core.interfaces.IImage)
class GalleryEntryImage(Image):
    """Image adapter for gallery entries (slides), that always uses the
    `original` variant and extracts its metadata from the slide, not the
    slide's image"""

    variant_id = 'original'

    @zeit.web.reify
    def _meta(self):
        return zeit.content.image.interfaces.IImageMetadata(self.context, None)

    @zeit.web.reify
    def layout(self):
        return self.context.layout


@grokcore.component.adapter(zeit.content.author.interfaces.IAuthor)
@grokcore.component.implementer(zeit.web.core.interfaces.IImage)
class AuthorImage(Image):
    """Image adapter for author objects enforcing `original` variants"""

    # XXX This should use a different variant, but author images currently
    # do not have a consistent ratio and framing of the portrayed person.
    # So we need to crop the lower part of the image using CSS, ignoring
    # the ratio.
    variant_id = 'original'

    # Author images shall not be filled with color.
    fill_color = None

    @zeit.web.reify
    def alt(self):
        author = self.context
        author_name = getattr(author, 'display_name', None)
        if author_name:
            return author_name
        else:
            return super(Image, self).alt


@grokcore.component.adapter(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.implementer(zeit.web.core.interfaces.IImage)
class ArticleModuleImage(Image):

    @zeit.web.reify
    def variant_id(self):
        if self.context.variant_id:
            return self.context.variant_id
        else:
            return super(ArticleModuleImage, self).variant_id


@grokcore.component.adapter(zeit.web.core.interfaces.INextread)
@grokcore.component.implementer(zeit.web.core.interfaces.IImage)
class NextreadImage(ArticleModuleImage):

    @zeit.web.reify
    def layout(self):
        return self.context.layout_id


@grokcore.component.adapter(zeit.content.cp.interfaces.ITeaserBlock)
@grokcore.component.implementer(zeit.web.core.interfaces.IImage)
class TeaserBlockImage(Image):

    @zeit.web.reify
    def variant_id(self):
        if self.context.layout.image_pattern:
            return self.context.layout.image_pattern
        else:
            return super(TeaserBlockImage, self).variant_id


def image_from_block_content(context):
    try:
        content = list(context)[0]
    except IndexError:
        raise zope.component.interfaces.ComponentLookupError(
            'Could not adapt as content', context,
            zeit.web.core.interfaces.IImage)
    image = zeit.web.core.interfaces.IImage(content, None)
    if image is not None:
        image.variant_id = context.layout.image_pattern
    return image


@zope.interface.implementer(zeit.content.image.interfaces.IImages)
class InMemoryImages(object):

    fill_color = None

    def __init__(self, context, image):
        self.context = context
        self.image = image


@grokcore.component.adapter(
    zeit.content.article.interfaces.IArticle)
@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
def images_from_article_with_fallback_body_image(context):
    # ZCA does not support "fall back to the next less specific adapter",
    # so we hardcode it.
    teaser_img = zeit.content.image.imagereference.ImagesAdapter(context)
    if teaser_img.image is not None or ILocalContent.providedBy(context):
        return teaser_img
    article_img = context.main_image.target
    return InMemoryImages(context, article_img)


@grokcore.component.adapter(
    zeit.web.core.article.ISeriesArticleWithFallbackImage)
@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
def images_from_series_with_fallback_image(context):
    # ZCA does not support "fall back to the next less specific adapter",
    # so we hardcode it.
    articleimg = zeit.content.image.imagereference.ImagesAdapter(context)
    if articleimg.image:
        return articleimg
    serie_cp = zeit.web.core.template.find_series_cp(context)
    return zeit.content.image.interfaces.IImages(serie_cp)


@grokcore.component.adapter(zeit.web.core.interfaces.IBlock,
                            name=u'content')
@grokcore.component.implementer(zeit.web.core.interfaces.IImage)
def image_from_article_block_content(context):
    return image_from_block_content(context)


@grokcore.component.adapter(zeit.content.cp.interfaces.ITeaserBlock,
                            name=u'content')
@grokcore.component.implementer(zeit.web.core.interfaces.IImage)
def image_from_teaser_block_content(context):
    return image_from_block_content(context)


@grokcore.component.adapter(zeit.web.core.centerpage.TeaserModule,
                            name=u'')
@grokcore.component.implementer(zeit.web.core.interfaces.IImage)
def image_from_teaser_module_content(context):
    return image_from_block_content(context)


@grokcore.component.adapter(zeit.web.core.block.Image)
@grokcore.component.implementer(zeit.web.core.interfaces.IImage)
class BlockImage(Image):

    def __init__(self, context):
        super(BlockImage, self).__init__(context)
        try:
            self._reference = zeit.cms.content.interfaces.IReference(
                self.context.context.references)
        except (AttributeError, TypeError):
            self._reference = None

    @zeit.web.reify
    def _meta(self):
        if zeit.content.image.interfaces.IImageMetadata.providedBy(
                self._reference):
            return self._reference

    @zeit.web.reify
    def variant_id(self):
        if self.context.variant_name:
            return self.context.variant_name
        else:
            return super(BlockImage, self).variant_id


@grokcore.component.adapter(zeit.web.core.block.HeaderImage)
@grokcore.component.implementer(zeit.web.core.interfaces.IImage)
class HeaderBlockImage(BlockImage):

    def __init__(self, context):
        super(HeaderBlockImage, self).__init__(context)
        article = zeit.content.article.interfaces.IArticle(
            self.context.context, None)
        if article is not None:
            self._a_supertitle = article.supertitle
            self._a_title = article.title
        else:
            self._a_supertitle = None
            self._a_title = None

    @zeit.web.reify
    def title(self):
        title = super(HeaderBlockImage, self).title
        if title:
            return title
        elif self.caption:
            return self.caption
        elif self._a_supertitle and self._a_title:
            return u'{}: {}'.format(self._a_supertitle, self._a_title)
        elif self._a_title:
            return self._a_title

    @zeit.web.reify
    def alt(self):
        alt = super(HeaderBlockImage, self).alt
        if alt:
            return alt
        elif self._a_supertitle and self.caption:
            return u'{}: {}'.format(self._a_supertitle, self.caption)
        elif self.caption:
            return self.caption
        elif self._a_supertitle and self._a_title:
            return u'{}: {}'.format(self._a_supertitle, self._a_title)
        elif self._a_title:
            return self._a_title


@grokcore.component.adapter(zeit.cms.content.interfaces.ICommonMetadata,
                            name=u'author')
@grokcore.component.implementer(zeit.web.core.interfaces.IImage)
def author_image_for_cmscontent(context):
    for author in context.authorships:
        image = zeit.web.core.interfaces.IImage(author.target, None)
        if image:
            return image
    raise zope.component.interfaces.ComponentLookupError(
        'Could not adapt as author', context, zeit.web.core.interfaces.IImage)


@grokcore.component.adapter(zeit.cms.interfaces.ICMSContent,
                            name=u'sharing')
@grokcore.component.implementer(zeit.web.core.interfaces.IImage)
def sharing_image_for_cmscontent(context):
    return zeit.web.core.interfaces.IImage(context)


@grokcore.component.adapter(zeit.content.article.interfaces.IArticle,
                            name=u'sharing')
@grokcore.component.implementer(zeit.web.core.interfaces.IImage)
def sharing_image_for_article(context):
    """Use a configured fallback image for breaking news articles
    that don't have an article image yet.
    """

    image = zeit.web.core.interfaces.IImage(context)

    if image.group is None and zeit.content.article.interfaces.IBreakingNews(
            context).is_breaking:
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        image.group = zeit.cms.interfaces.ICMSContent(
            conf['breaking_news_fallback_image'], None)
    elif zeit.web.core.article.IColumnArticle.providedBy(context):
        image = zope.component.queryAdapter(
            context, zeit.web.core.interfaces.IImage, 'author')

    if not image:
        raise zope.component.interfaces.ComponentLookupError(
            'Could not adapt as sharing', context,
            zeit.web.core.interfaces.IImage)
    return image


class SyntheticImageGroup(zeit.content.image.imagegroup.ImageGroup,
                          zeit.cms.repository.repository.Container):

    def __init__(self, context):
        super(SyntheticImageGroup, self).__init__()
        self.context = context

    def __getitem__(self, key):
        return self.create_variant_image(key)

    def __repr__(self):
        return object.__repr__(self)

    def __len__(self):
        return int(bool(self.master_image))

    def __contains__(self, key):
        # Synthetic image groups *only* contain one master image.
        return False

    def keys(self):
        return ()

    @property
    def master_image(self):
        raise NotImplementedError


# NOTE: Maybe we want to determine whether our lonesome image is actually
#       contained in a group and then return that instead of synthesizing one.
@grokcore.component.implementer(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.adapter(zeit.content.image.interfaces.IImage)
class LocalImageGroup(SyntheticImageGroup):

    def __init__(self, context):
        super(LocalImageGroup, self).__init__(context)
        self.uniqueId = u'{}/imagegroup/'.format(context.uniqueId)

    @zeit.web.reify
    def master_image(self):
        return self.context


class RemoteImage(object):

    KiB = 1024
    DOWNLOAD_CHUNK_SIZE = 2 * KiB

    def __init__(self, url):
        if not isinstance(url, basestring):
            raise TypeError('Remote image URL needs to be string formatted')
        self.url = url
        # Allow tests to load Brightcove images locally (XXX test-only code,
        # but it's still better than depending on Brightcove/HTTP in tests).
        if '%DATA%' in self.url:
            self.url = self.url.replace(
                '%DATA%', pkg_resources.resource_filename(
                    'zeit.web.core', 'data'))
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
        response = None
        try:
            with zeit.web.core.metrics.http(
                    'zeit.web.core.video.thumbnail.brightcove') as record:
                response = session.get(
                    self.url, stream=True,
                    timeout=conf.get('brightcove_image_timeout', 2))
                record(response)
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


class RemoteImageGroup(SyntheticImageGroup,
                       zeit.cms.repository.repository.Container):

    def __new__(cls, context):
        if not cls.get_image_url(context):
            return None
        return super(RemoteImageGroup, cls).__new__(cls, context)

    def __init__(self, context):
        super(RemoteImageGroup, self).__init__(context)
        self.image_url = self.get_image_url(context)

    # We cannot use a property/reify since we need this already in __new__.
    @classmethod
    def get_image_url(cls, context):
        # This API applies to most of our subclasses, so it's not worth raising
        # NotImplementedError here only to have each of them copy this down.
        return context.image_url

    uniqueId = NotImplemented

    @zeit.web.reify
    def master_image(self):
        try:
            return RemoteImage(self.image_url)
        except TypeError:
            return


@grokcore.component.implementer(zeit.content.image.interfaces.IImageMetadata)
@grokcore.component.adapter(RemoteImageGroup)
class RemoteImageMetaData(object):

    def __init__(self, group):
        iface = zeit.content.image.interfaces.IImageMetadata
        for field in iface:
            try:
                setattr(self, field, iface[field].missing_value)
            except AttributeError:
                continue
        if group.__parent__ is not None:
            self.alt = group.__parent__.title
            self.caption = group.__parent__.text
            self.title = group.__parent__.title


# Baseclass, register this as an adapter at the concrete usage points.
@zope.interface.implementer(zeit.content.image.interfaces.IImages)
class RemoteImages(object):

    fill_color = None

    def __init__(self, context):
        self.context = context
        self.image = zeit.content.image.interfaces.IImageGroup(context, None)


@grokcore.component.implementer(zeit.content.image.interfaces.IMasterImage)
@grokcore.component.adapter(SyntheticImageGroup)
def syntheticimagegroup_to_masterimage(group):
    return group.master_image


@grokcore.component.implementer(zeit.content.image.interfaces.ITransform)
@grokcore.component.adapter(RemoteImage)
def remoteimage_to_imagetransform(image):
    return zeit.content.image.transform.ImageTransform(image)


class ImageExpiration(grokcore.component.Adapter):

    grokcore.component.context(zeit.content.image.interfaces.IImageGroup)
    grokcore.component.implements(zeit.web.core.interfaces.IExpiration)

    @property
    def seconds(self):
        workflow = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        if not workflow.released_to:
            return None
        now = datetime.datetime.now(pytz.UTC)
        return int((workflow.released_to - now).total_seconds())

    @property
    def is_expired(self):
        if self.seconds is None:
            return False
        return self.seconds < 0


@grokcore.component.adapter(zeit.content.image.interfaces.IImage)
@grokcore.component.implementer(zeit.web.core.interfaces.IExpiration)
def single_image_expiration(context):
    return zeit.web.core.interfaces.IExpiration(context.__parent__, None)


@grokcore.component.adapter(zeit.web.core.interfaces.IImage)
@grokcore.component.implementer(zeit.web.core.interfaces.IExpiration)
def web_image_expiration(context):
    return zeit.web.core.interfaces.IExpiration(context.group, None)


class VariantSource(zeit.content.image.variant.VariantSource):

    DEFAULT_NAME = 'original'
    product_configuration = 'zeit.content.image'
    config_url = 'variant-source'

    def find(self, context, variant_id=DEFAULT_NAME):
        mapping = self._get_mapping()
        tree = self._get_tree()
        mapped = mapping.get(variant_id, variant_id)
        for node in tree.iterchildren('*'):
            if not self.isAvailable(node, context):
                continue
            attributes = dict(node.attrib)
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
