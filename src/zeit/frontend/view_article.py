import datetime
import logging

from pyramid.decorator import reify
from pyramid.renderers import render_to_response
from pyramid.view import view_config
import pyramid.httpexceptions

import zeit.content.article.edit.interfaces
from zeit.content.author.interfaces import IAuthorReference
from zeit.magazin.interfaces import IArticleTemplateSettings
import zeit.connector.connector
import zeit.connector.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.image.interfaces

import zeit.frontend.interfaces
import zeit.frontend.reach
import zeit.frontend.article
import zeit.frontend.comments
import zeit.frontend.view

log = logging.getLogger(__name__)


def register_copyrights(func):
    def wrapped(self):
        container = func(self)
        if container:
            for t in zeit.frontend.interfaces.ITeaserSequence(container):
                if not t.image:
                    continue
                self._copyrights.setdefault(t.image.image_group, t.image)
        return container
    return wrapped


@view_config(context=zeit.content.article.interfaces.IArticle,
             renderer='templates/article.html')
@view_config(context=zeit.content.article.interfaces.IArticle,
             name='komplettansicht',
             renderer='templates/article_komplett.html')
class Article(zeit.frontend.view.Content):

    advertising_enabled = True
    is_longform = False
    main_nav_full_width = False
    page_nr = 1

    def __init__(self, *args, **kwargs):
        super(Article, self).__init__(*args, **kwargs)
        self._copyrights = {}

    def __call__(self):
        self.context.advertising_enabled = self.advertising_enabled
        self.context.main_nav_full_width = self.main_nav_full_width
        self.context.is_longform = self.is_longform
        self.context.current_year = datetime.date.today().year

        if IArticleTemplateSettings(self.context).template == 'photocluster':
            self.context.advertising_enabled = False
            return render_to_response('templates/photocluster.html',
                                      {'view': self},
                                      request=self.request)
        return {}

    @reify
    def template(self):
        return IArticleTemplateSettings(self.context).template or 'default'

    @reify
    def header_layout(self):
        return IArticleTemplateSettings(self.context).header_layout or \
            'default'

    @reify
    def pages(self):
        return zeit.frontend.interfaces.IPages(self.context)

    @reify
    def current_page(self):
        return self.pages[0]

    @reify
    def next_title(self):
        if self.page_nr < len(self.pages):
            return self.pages[self.page_nr].teaser

    @reify
    def article_url(self):
        path = '/'.join(self.request.traversed)
        return self.request.route_url('home') + path

    @reify
    def pages_urls(self):
        urls = []
        for number in range(0, len(self.pages)):
            url = self.article_url
            if number > 0:
                url += '/seite-' + str(number + 1)
            urls.append(url)
        return urls

    @reify
    def next_page_url(self):
        actual_index = self.page_nr - 1
        total = len(self.pages)
        return self.pages_urls[actual_index + 1] \
            if actual_index + 1 < total else None

    @reify
    def prev_page_url(self):
        actual_index = self.page_nr - 1
        return self.pages_urls[actual_index - 1] \
            if actual_index - 1 >= 0 else None

    @reify
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

    @reify
    def select_first_body_obj(self):
        body = zeit.content.article.edit.interfaces.IEditableBody(self.context)
        return body.values().pop(0) if len(body.values()) > 0 else None

    def _create_obj(self, _cls, obj):
        try:
            return _cls(obj)
        except OSError:
            log.debug('Object does not exist.')

    @reify
    def header_img(self):
        obj = self.select_first_body_obj
        if zeit.content.article.edit.interfaces.IImage.providedBy(obj):
            return zeit.frontend.block.HeaderImageStandard(obj)

    @reify
    def header_video(self):
        obj = self.select_first_body_obj
        if zeit.content.article.edit.interfaces.IVideo.providedBy(obj):
            return self._create_obj(zeit.frontend.block.HeaderVideo, obj)

    @reify
    def first_img(self):
        obj = self.select_first_body_obj
        if zeit.content.article.edit.interfaces.IImage.providedBy(obj):
            return self._create_obj(zeit.frontend.block.Image, obj)

    @reify
    def header_elem(self):
        return self.header_video or self.header_img

    @reify
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
            'location': ', ' + IAuthorReference(author_ref).location
            if IAuthorReference(author_ref).location and
            IArticleTemplateSettings(self.context).template
            != 'longform' else '',
        }

    @reify
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
                        result['suffix'] = ' und'
                    elif index < len(author_ref) - 1:
                        result['suffix'] = ', '
                    authorList.append(result)
            return authorList
        except (IndexError, OSError):
            return None

    @reify
    def authorsList(self):
        if self.authors:
            return ';'.join([rt['name'] for rt in self.authors])

    @reify
    def twitter_card_type(self):
        if IArticleTemplateSettings(self.context).template == 'longform':
            return 'summary_large_image'
        else:
            return 'summary'

    @reify
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
            return prefix + ' ' + self.context.genre.title()
        else:
            return None

    @reify
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

    @reify
    def location(self):
        return None  # XXX not implemented in zeit.content.article yet

    @reify
    @register_copyrights
    def nextread(self):
        nextread = zeit.frontend.interfaces.INextreadTeaserBlock(self.context)
        if not len(nextread.teasers):
            nextread = None
        return nextread

    @reify
    def comments(self):
        return zeit.frontend.comments.get_thread(
            unique_id=self.context.uniqueId, request=self.request)

    @reify
    def serie(self):
        if self.context.serie:
            return self.context.serie.lower()

    @reify
    def linkreach(self):
        def unitize(n):
            if n <= 999:
                return str(n), ''
            elif n <= 9999:
                return ','.join(list(str(n))[:2]), 'Tsd.'
            elif n <= 999999:
                return str(n / 1000), 'Tsd.'
            else:
                return str(n / 1000000), 'Mio.'

        linkreach = self.request.registry.settings.linkreach_host
        reach = zeit.frontend.reach.LinkReach(None, linkreach)
        raw = reach.get_counts_by_url(self.article_url)
        total = raw.pop('total', 0)
        counts = {'total': unitize(total)} if total >= 10 else {}
        for k, v in raw.items():
            try:
                counts[k] = unitize(v['total'])
            except:
                continue
        return counts

    @reify
    def tracking_type(self):
        if self.type == 'article':
            return 'Artikel'

    @reify
    def text_length(self):
        return self.context.textLength

    @reify
    def copyrights(self):
        teaser_list = []
        for teaser in self._copyrights.itervalues():
            if len(teaser.copyright[0][0]) <= 1:
                # Drop teaser if no copyright text is assigned.
                continue
            teaser_list.append(
                dict(
                    label=teaser.copyright[0][0],
                    image=zeit.frontend.template.translate_url(
                        self.context, teaser.src),
                    link=teaser.copyright[0][1],
                    nofollow=teaser.copyright[0][2]
                )
            )
        return sorted(teaser_list, key=lambda k: k['label'])


@view_config(context=zeit.content.article.interfaces.IArticle,
             name='seite',
             path_info='.*seite-[0-9]+$',
             renderer='templates/article.html')
class ArticlePage(Article):

    def __call__(self):
        super(ArticlePage, self).__call__()
        if self.request.view_name == 'komplettansicht':
            return {}

        if self.page_nr > len(self.pages):
            raise pyramid.httpexceptions.HTTPNotFound()
        return {}

    @reify
    def page_nr(self):
        try:
            n = int(self.request.path_info.split('/')[-1][6:])
            if n == 1:
                raise pyramid.httpexceptions.HTTPNotFound()
            return n
        except (IndexError, ValueError):
            raise pyramid.httpexceptions.HTTPNotFound()

    @reify
    def current_page(self):
        return zeit.frontend.interfaces.IPages(self.context)[self.page_nr - 1]

    @reify
    def next_title(self):
        pages = zeit.frontend.interfaces.IPages(self.context)
        if self.page_nr < len(pages):
            return pages[self.page_nr].teaser


@view_config(context=zeit.frontend.article.ILongformArticle,
             renderer='templates/longform.html')
class LongformArticle(Article):

    advertising_enabled = False
    main_nav_full_width = True
    is_longform = True

    @reify
    def header_img(self):
        obj = self.select_first_body_obj
        if zeit.content.article.edit.interfaces.IImage.providedBy(obj):
            return self._create_obj(zeit.frontend.block.HeaderImage, obj)


@view_config(context=zeit.frontend.article.IShortformArticle,
             renderer='templates/shortform.html')
class ShortformArticle(Article):
    pass


@view_config(context=zeit.frontend.article.IColumnArticle,
             renderer='templates/column.html')
class ColumnArticle(Article):
    pass


@view_config(name='teaser',
             context=zeit.content.article.interfaces.IArticle,
             renderer='templates/teaser.html')
class Teaser(Article):

    @reify
    def teaser_text(self):
        return self.context.teaser
