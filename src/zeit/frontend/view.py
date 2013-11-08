from pyramid.view import view_config
import zeit.frontend.model
from babel.dates import get_timezone


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
        return tz.localize(self.context.publish_date)


@view_config(route_name='json',
             context=zeit.frontend.model.Content,
             renderer='json')
@view_config(context=zeit.frontend.model.Content,
             renderer='templates/article.html')
class Article(Base):

    @property
    def lead_pic(self):
        return self.context.lead_pic

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
        return self.context.pages

    @property
    def header_img(self):
        return self.context.header_img

    @property
    def author(self):
        return self.context.author

    @property
    def publish_date(self):
        return self.context.publish_date

    @property
    def last_modified_date(self):
        return self.context.last_modified_date

    @property
    def rankedTags(self):
        return self.context.rankedTags

    @property
    def genre(self):
        return self.context.genre

    @property
    def source(self):
        return self.context.source

    @property
    def location(self):
        return self.context.location


class Gallery(Base):
    pass


@view_config(route_name='json',
             context=zeit.frontend.model.Content,
             renderer='json', name='teaser')
@view_config(name='teaser',
             context=zeit.frontend.model.Content,
             renderer='templates/teaser.html')
class Teaser(Article):

    @property
    def teaser_text(self):
        """docstring for teaser"""
        return self.context.teaser
