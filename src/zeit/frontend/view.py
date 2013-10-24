from pyramid.view import view_config
import zeit.frontend.model


class Base(object):

    """Base class for all views."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return {}


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
    def header_img_src(self):
        return self.context.header_img_src


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
