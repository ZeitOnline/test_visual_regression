from pyramid.view import view_config
import zeit.frontend.model
from babel.dates import get_timezone
from pyramid.renderers import render_to_response


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


_navigation = {'start': ('Start', 'http://www.zeit.de/index', 'myid1'),
               'lebensart': (
                   'ZEIT Magazin',
                   'http://www.zeit.de/magazin/index',
                   'myid2',
               ),
               'mode': (
                   'Mode',
                   'http://www.zeit.de/magazin/lebensart/index',
                   'myid3',
               ), }


@view_config(route_name='json',
             context=zeit.frontend.model.Content,
             renderer='json')
@view_config(context=zeit.frontend.model.Content,
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
    def subpage_index(self):
        return self.context.subpage_index

    @property
    def header_img(self):
        return self.context.header_img

    @property
    def author(self):
        return self.context.author

    @property
    def publish_date(self):
        tz = get_timezone('Europe/Berlin')
        return self.context.publish_date.astimezone(tz)

    @property
    def publish_date_meta(self):
        return self.context.publish_date_meta

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

    @property
    def focussed_nextread(self):
        return self.context.focussed_nextread

    def breadcrumb(self):
        l = [_navigation['start']]
        if self.context.ressort in _navigation:
            l.append(_navigation[self.context.ressort])
        if self.context.sub_ressort in _navigation:
            l.append(_navigation[self.context.sub_ressort])
        if self.title:
            l.append((self.title, 'http://localhost'))
        return l


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
