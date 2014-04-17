from babel.dates import get_timezone
from datetime import date
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.article.edit.interfaces import IImage
from zeit.content.article.edit.interfaces import IVideo
from zeit.content.author.interfaces import IAuthorReference
from zeit.content.image.interfaces import IImageMetadata
from zeit.magazin.interfaces import IArticleTemplateSettings, INextRead
from zope.component import providedBy
import logging
import zeit.connector.connector
import zeit.connector.interfaces
import zeit.content.cp.interfaces
import zeit.content.article.interfaces
import zeit.content.image.interfaces
import zeit.frontend.article
import pyramid.httpexceptions
from .comments import get_thread

log = logging.getLogger(__name__)


_navigation = {'start': ('Start', 'http://www.zeit.de/index', 'myid1'),
               'zmo': ('ZEIT Magazin', 'http://www.zeit.de/index', 'myid_zmo'),
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


@view_config(context=zeit.content.article.interfaces.IArticle,
             renderer='templates/article.html')
@view_config(context=zeit.content.article.interfaces.IArticle,
             name='komplettansicht',
             renderer='templates/article_komplett.html')
class Article(zeit.frontend.view.Base):

    advertising_enabled = True
    main_nav_full_width = False
    is_longform = False
    page_nr = 1

    def __call__(self):
        self.context.advertising_enabled = self.advertising_enabled
        self.context.main_nav_full_width = self.main_nav_full_width
        self.context.is_longform = self.is_longform
        self.context.current_year = date.today().year
        self.comments = self._comments()

        if IArticleTemplateSettings(self.context).template == 'photocluster':
            self.context.advertising_enabled = False
            return render_to_response('templates/photocluster.html',
                                      {"view": self},
                                      request=self.request)
        return {}

    @property
    def title(self):
        return self.context.title

    @property
    def template(self):
        template = IArticleTemplateSettings(self.context).template
        return template if template is not None else "default"

    @property
    def header_layout(self):
        layout = IArticleTemplateSettings(self.context).header_layout
        return layout if layout is not None else "default"

    @property
    def subtitle(self):
        return self.context.subtitle

    @property
    def supertitle(self):
        return self.context.supertitle

    @property
    def pagetitle(self):
        if self.context.supertitle:
            return self.context.supertitle + ': ' + self.context.title
        else:
            return self.context.title

    @property
    def pagedescription(self):
        return self.context.subtitle

    @property
    def pages(self):
        return zeit.frontend.interfaces.IPages(self.context)

    @property
    def current_page(self):
        return self.pages[0]

    @property
    def next_title(self):
        try:
            return self.pages[self.page_nr].teaser
        except (IndexError):
            return ''

    @property
    def article_url(self):
        path = '/'.join(self.request.traversed)
        return self.request.route_url('home') + path

    @property
    def pages_urls(self):
        _pages_urls = []
        for number in range(0, len(self.pages)):
            url = self.article_url
            if number > 0:
                url += '/seite-' + str(number+1)
            _pages_urls.append(url)
        return _pages_urls

    @property
    def next_page_url(self):
        _actual_index = self.page_nr - 1
        total = len(self.pages)
        return self.pages_urls[_actual_index + 1] if _actual_index + 1 < total else None

    @property
    def prev_page_url(self):
        actual_index = self.page_nr - 1
        return self.pages_urls[actual_index - 1] if actual_index-1 >= 0 else None

    @property
    def pagination(self):
        return {
            'current': self.page_nr,
            'total': len(self.pages),
            'next_page_title': self.next_title,
            'article_url': self.article_url,
            'pages_urls': self.pages_urls,
            'next_page_url': self.next_page_url,
            'prev_page_url': self.prev_page_url
        }

    @property
    def _select_first_body_obj(self):
        body = zeit.content.article.edit.interfaces.IEditableBody(self.context)
        return body.values().pop(0) if len(body.values()) > 0 else None

    def _create_obj(self, _cls, obj):
        try:
            return _cls(obj)
        except OSError:
            log.debug("Object does not exist.")

    @property
    def header_img(self):
        obj = self._select_first_body_obj
        if IImage in providedBy(obj):
            return zeit.frontend.block.HeaderImageStandard(obj)

    @property
    def header_video(self):
        obj = self._select_first_body_obj
        if IVideo in providedBy(obj):
            return self._create_obj(zeit.frontend.block.HeaderVideo, obj)

    @property
    def first_img(self):
        obj = self._select_first_body_obj
        if IImage in providedBy(obj):
            return self._create_obj(zeit.frontend.block.Image, obj)

    @property
    def header_elem(self):
        if self.header_video is not None:
            return self.header_video
        return self.header_img

    @property
    def sharing_img(self):
        if self.header_img is not None:
            return self.header_img
        if self.header_video is not None:
            return self.header_video
        else:
            return self.first_img

    def _get_author(self, index):
        try:
            author = index.target
            author_ref = index
        except (IndexError, OSError):
            author = None
        return {
            'name': author.display_name if author else None,
            'href': author.uniqueId if author else None,
            'suffix': '',
            'prefix': '',
            'location': ", " + IAuthorReference(author_ref).location
            if IAuthorReference(author_ref).location and
            IArticleTemplateSettings(self.context).template
            != 'longform' else '',
        }

    @property
    def authors(self):
        authorList = []
        try:
            author_ref = self.context.authorships
            for index, author in enumerate(author_ref):
                result = self._get_author(author)
                if result is not None:
                    # add prefix
                    if index == 0:
                        if IArticleTemplateSettings(self.context).template \
                           == 'longform':
                            result['prefix'] = u'\u2014' + ' von'
                        else:
                            result['prefix'] = ' von'
                    # add suffix
                    if index == len(author_ref) - 2:
                        result['suffix'] = " und"
                    elif index < len(author_ref) - 1:
                        result['suffix'] = ", "
                    authorList.append(result)
            return authorList
        except (IndexError, OSError):
            return None

    @property
    def twitter_card_type(self):
        if IArticleTemplateSettings(self.context).template == 'longform':
            return 'summary_large_image'
        else:
            return 'summary'

    @property
    def date_first_released(self):
        tz = get_timezone('Europe/Berlin')
        date = IPublishInfo(
            self.context).date_first_released
        if date:
            return date.astimezone(tz)

    @property
    def date_first_released_meta(self):
        return IPublishInfo(
            self.context).date_first_released.isoformat()

    @property
    def date_last_published_semantic(self):
        tz = get_timezone('Europe/Berlin')
        date = IPublishInfo(self.context).date_last_published_semantic
        if self.date_first_released is not None and date is not None:
            if date > self.date_first_released:
                return date.astimezone(tz)
            else:
                return None

    def _get_date_format(self):
        if self.context.product:
            if self.context.product.id == 'ZEI' or \
               self.context.product.id == 'ZMLB':
                return 'short'
            else:
                return 'long'
        else:
            return 'long'

    @property
    def show_date_format(self):
        if self.date_last_published_semantic:
            return 'long'
        else:
            return self._get_date_format()

    @property
    def show_date_format_seo(self):
        return self._get_date_format()

    @property
    def show_article_date(self):
        if self.date_last_published_semantic:
            return self.date_last_published_semantic
        else:
            return self.date_first_released

    @property
    def rankedTags(self):
        return self.context.keywords

    @property
    def rankedTagsList(self):
        keyword_list = ''
        if self.rankedTags:
            for keyword in self.context.keywords:
                keyword_list += keyword.label + ';'
            return keyword_list[:-1]
        else:
            return ''

    @property
    def genre(self):
        # TODO: remove prose list, if integration of article-genres.xml
        # is clear (as)
        prefix = 'ein'
        if (self.context.genre == 'glosse') or \
           (self.context.genre == 'reportage') or \
           (self.context.genre == 'nachricht') or \
           (self.context.genre == 'analyse'):
            prefix = 'eine'
        if self.context.genre:
            return prefix + " " + self.context.genre.title()
        else:
            return None

    @property
    def source(self):
        # TODO: find sth more elegant (as)
        # 1. dont know why source stays empty if default value wasnt changed
        # 2. issue/year will only be shown for Z and ZM right now
        # because there's alway a value in volume and year
        source = None
        if self.context.product:
            if self.context.product.id == 'ZEI' or \
               self.context.product.id == 'ZMLB':
                source = self.context.product_text + ' Nr. ' \
                    + str(self.context.volume) + '/' + \
                    str(self.context.year)
            elif self.context.product.id != 'ZEDE':
                source = self.context.product_text
        elif self.context.product_text:
            source = self.context.product_text
        return self.context.copyrights or source

    @property
    def location(self):
        return None  # XXX not implemented in zeit.content.article yet

    @property
    def focussed_nextread(self):
        nextread = INextRead(self.context)
        related = nextread.nextread[0]
        if related:
            try:
                _layout = related.nextread_layout
            except AttributeError:
                _layout = 'base'
            try:
                image = related.main_image
                image = {
                    'uniqueId': image.uniqueId,
                    'caption': (related.main_image_block.custom_caption
                                or IImageMetadata(image).caption)}
            except AttributeError:
                image = {'uniqueId': None}
                _layout = 'minimal'
            read = {'layout': _layout,
                    'article': related,
                    'image': image}
            return read

    @property
    def breadcrumb(self):
        l = [_navigation['start']]
        l.append(_navigation['zmo'])
        if self.context.ressort in _navigation:
            l.append(_navigation[self.context.ressort])
        if self.context.sub_ressort in _navigation:
            l.append(_navigation[self.context.sub_ressort])
        if self.title:
            l.append((self.title, 'http://localhost'))
        return l

    def _comments(self):
        return get_thread(unique_id=self.context.uniqueId,
                          request=self.request)

    @property
    def tracking_type(self):
        if type(self.context).__name__.lower() == 'article':
            return 'Artikel'

    @property
    def type(self):
        return type(self.context).__name__.lower()

    @property
    def ressort(self):
        if self.context.ressort:
            return self.context.ressort.lower()
        else:
            return ''

    @property
    def sub_ressort(self):
        if self.context.sub_ressort:
            return self.context.sub_ressort.lower()
        else:
            return ''

    @property
    def text_length(self):
        return self.context.textLength

    @property
    def banner_channel(self):
        channel = ''
        if self.ressort:
            channel += self.ressort
        if self.sub_ressort:
            channel += "/" + self.sub_ressort
        if self.type:
            channel += "/" + self.type
        return channel


    def banner(self, tile):
        try:
            return zeit.frontend.banner.banner_list[tile-1]
        except IndexError:
            return None



@view_config(context=zeit.content.article.interfaces.IArticle,
             name='seite',
             path_info='.*seite-[0-9]+$',
             renderer='templates/article.html')
class ArticlePage(Article):

    def __call__(self):
        super(ArticlePage, self).__call__()
        if self.request.view_name == 'komplettansicht':
            return {}

        pages_in_article = len(self.pages)

        if self.page_nr > pages_in_article:
            raise pyramid.httpexceptions.HTTPNotFound()
        return {}

    @property
    def page_nr(self):
        try:
            n = int(self.request.path_info.split("/")[-1][6:])
            if n == 1:
                raise pyramid.httpexceptions.HTTPNotFound()
            return n
        except (IndexError, ValueError):
            raise pyramid.httpexceptions.HTTPNotFound()

    @property
    def current_page(self):
        return zeit.frontend.interfaces.IPages(self.context)[self.page_nr-1]

    @property
    def next_title(self):
        try:
            page = zeit.frontend.interfaces.IPages(self.context)[self.page_nr]
            return page.teaser
        except (IndexError):
            return ''


@view_config(context=zeit.frontend.article.ILongformArticle,
             renderer='templates/longform.html')
class LongformArticle(Article):

    advertising_enabled = False
    main_nav_full_width = True
    is_longform = True

    @property
    def header_img(self):
        obj = self._select_first_body_obj
        if IImage in providedBy(obj):
            return self._create_obj(zeit.frontend.block.HeaderImage, obj)


@view_config(context=zeit.frontend.article.IShortformArticle,
             renderer='templates/shortform.html')
class ShortformArticle(Article):
    pass


@view_config(name='teaser',
             context=zeit.content.article.interfaces.IArticle,
             renderer='templates/teaser.html')
class Teaser(Article):

    @property
    def teaser_text(self):
        """docstring for teaser"""
        return self.context.teaser
