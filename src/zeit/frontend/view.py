from babel.dates import get_timezone
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from zeit.cms.related.interfaces import IRelatedContent
from zeit.cms.workflow.interfaces import IPublishInfo, IModified
from zeit.content.image.interfaces import IImageMetadata
import zeit.content.article.interfaces


class Base(object):
    """Base class for all views."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return {}

    @property
    def publish_date(self):
        tz = get_timezone('Europe/Berlin')
        return self.context.publish_date.astimezone(tz)


@view_config(route_name='json',
             context=zeit.content.article.interfaces.IArticle,
             renderer='json')
@view_config(context=zeit.content.article.interfaces.IArticle,
             renderer='templates/article.html')
class Article(Base):

    def __call__(self):
        self.context.advertising_enabled = True
        self.context.main_nav_full_width = False
        if self.context.template == 'longform':
            self.context.advertising_enabled = False
            self.context.main_nav_full_width = True
            return render_to_response('templates/longform.html',
                                      {"view": self},
                                      request=self.request)
        return {}

    @property
    def title(self):
        return self.context.title

    @property
    def subtitle(self):
        return self.context.subtitle

    @property
    def supertitle(self):
        return self.context.supertitle

    @property
    def pages(self):
        return zeit.frontend.interfaces.IPages(self.context)

    @property
    def header_img(self):
        return self.context.header_img

    @property
    def author(self):
        try:
            author = self.context.authors[0]
        except IndexError:
            author = None
        return {
            'name': author.display_name if author else None,
            'href': author.uniqueId if author else None,
            'prefix': " von " if self.context.genre else "Von ",
            'suffix': ', ' if self.location else None,
        }

    @property
    def publish_date(self):
        tz = get_timezone('Europe/Berlin')
        return IPublishInfo(
            self.context).date_last_published_semantic.astimezone(tz)

    @property
    def publish_date_meta(self):
        return IPublishInfo(
            self.context).date_last_published_semantic.isoformat()

    @property
    def last_modified_date(self):
        return IModified(self.context).date_last_modified

    @property
    def rankedTags(self):
        return self.context.keywords

    @property
    def genre(self):
        return self.context.genre

    @property
    def source(self):
        return self.context.copyrights or self.context.product_text

    @property
    def location(self):
        return None  # XXX not implemented in zeit.content.article yet

    @property
    def focussed_nextread(self):
        # XXX nextread is not implemented in zeit.content.article yet, so we'll
        # use relateds for the time being
        related = IRelatedContent(self.context).related
        if related:
            related = related[0]
            image = related.main_image
            if image is not None:
                image = {
                    'uniqueId': image.uniqueId,
                    'caption': (related.main_image_block.custom_caption
                                or IImageMetadata(image).caption),
                }
            return {'layout': 'base',  # XXX not implemented
                    'article': related,
                    'image': image}


class Gallery(Base):
    pass


@view_config(route_name='json',
             context=zeit.content.article.interfaces.IArticle,
             renderer='json', name='teaser')
@view_config(name='teaser',
             context=zeit.content.article.interfaces.IArticle,
             renderer='templates/teaser.html')
class Teaser(Article):

    @property
    def teaser_text(self):
        """docstring for teaser"""
        return self.context.teaser
