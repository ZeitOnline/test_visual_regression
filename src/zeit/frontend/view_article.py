import datetime
import itertools
import logging
import re

from pyramid.view import view_config
import pyramid.httpexceptions

from zeit.content.author.interfaces import IAuthorReference
from zeit.magazin.interfaces import IArticleTemplateSettings
import zeit.connector.connector
import zeit.connector.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.content.image.interfaces

import zeit.frontend
import zeit.frontend.article
import zeit.frontend.comments
import zeit.frontend.interfaces
import zeit.frontend.reach
import zeit.frontend.template
import zeit.frontend.view

log = logging.getLogger(__name__)


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
        self.context.advertising_enabled = self.advertising_enabled
        self.context.main_nav_full_width = self.main_nav_full_width
        self.context.is_longform = self.is_longform
        self.context.current_year = datetime.date.today().year

    @zeit.frontend.reify
    def template(self):
        return IArticleTemplateSettings(self.context).template or 'default'

    @zeit.frontend.reify
    def header_layout(self):
        return IArticleTemplateSettings(self.context).header_layout or \
            'default'

    @zeit.frontend.reify
    def pages(self):
        return zeit.frontend.interfaces.IPages(self.context)

    @zeit.frontend.reify
    def current_page(self):
        return self.pages[0]

    @zeit.frontend.reify
    def next_title(self):
        if self.page_nr < len(self.pages):
            return self.pages[self.page_nr].teaser

    @zeit.frontend.reify
    def article_url(self):
        path = '/'.join(self.request.traversed)
        return self.request.route_url('home') + path

    @zeit.frontend.reify
    def pages_urls(self):
        urls = []
        for number in range(0, len(self.pages)):
            url = self.article_url
            if number > 0:
                url += '/seite-' + str(number + 1)
            urls.append(url)
        return urls

    @zeit.frontend.reify
    def next_page_url(self):
        actual_index = self.page_nr - 1
        return self.pages_urls[actual_index + 1] \
            if actual_index + 1 < len(self.pages) else None

    @zeit.frontend.reify
    def prev_page_url(self):
        actual_index = self.page_nr - 1
        return self.pages_urls[actual_index - 1] \
            if actual_index - 1 >= 0 else None

    @zeit.frontend.reify
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

    @zeit.frontend.reify
    def first_body_obj(self):
        body = zeit.content.article.edit.interfaces.IEditableBody(self.context)
        return body.values().pop(0) if len(body.values()) > 0 else None

    def _create_obj(self, _cls, obj):
        try:
            return _cls(obj)
        except OSError:
            log.debug('Object does not exist.')

    @zeit.frontend.reify
    def header_img(self):
        obj = self.first_body_obj
        if zeit.content.article.edit.interfaces.IImage.providedBy(obj):
            img = zeit.frontend.block.HeaderImageStandard(obj)
            if img:
                try:
                    self._copyrights.setdefault(img.uniqueId, img)
                except AttributeError:
                    pass
            return img

    @zeit.frontend.reify
    def header_video(self):
        obj = self.first_body_obj
        if zeit.content.article.edit.interfaces.IVideo.providedBy(obj):
            return self._create_obj(zeit.frontend.block.HeaderVideo, obj)

    @zeit.frontend.reify
    def first_img(self):
        obj = self.first_body_obj
        if zeit.content.article.edit.interfaces.IImage.providedBy(obj):
            return self._create_obj(zeit.frontend.block.Image, obj)

    @zeit.frontend.reify
    def header_elem(self):
        return self.header_video or self.header_img

    @zeit.frontend.reify
    def resource_url(self):
        return self.request.resource_url(self.context).rstrip('/')

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

    @zeit.frontend.reify
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

    @zeit.frontend.reify
    def authorsList(self):
        if self.authors:
            return ';'.join([rt['name'] for rt in self.authors])

    @zeit.frontend.reify
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

    @zeit.frontend.reify
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

    @zeit.frontend.reify
    def location(self):
        return None  # XXX not implemented in zeit.content.article yet

    @property
    def nextread(self):
        nextread = zeit.frontend.interfaces.INextreadTeaserBlock(self.context)
        if not nextread.teasers:
            return
        if nextread.layout != 'minimal':
            for i in zeit.frontend.interfaces.ITeaserSequence(nextread):
                i.image and self._copyrights.setdefault(
                    i.image.image_group, i.image)
        return nextread

    @zeit.frontend.reify
    def comments(self):
        return zeit.frontend.comments.get_thread(
            unique_id=self.context.uniqueId, request=self.request)

    @zeit.frontend.reify
    def serie(self):
        if self.context.serie:
            return self.context.serie.lower()

    @zeit.frontend.reify
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

    @zeit.frontend.reify
    def tracking_type(self):
        if self.type == 'article':
            return 'Artikel'

    @zeit.frontend.reify
    def text_length(self):
        return self.context.textLength

    @property
    def copyrights(self):
        for i in (self.is_longform and itertools.chain(*self.pages) or
                  self.current_page):
            if hasattr(i, 'copyright') and hasattr(i, 'uniqueId'):
                self._copyrights.setdefault(i.uniqueId, i)

        cr_list = []
        for i in self._copyrights.itervalues():
            if len(i.copyright[0][0]) > 1:
                cr_list.append(
                    dict(
                        label=i.copyright[0][0],
                        image=zeit.frontend.template.translate_url(i.src),
                        link=i.copyright[0][1],
                        nofollow=i.copyright[0][2]
                    )
                )
        return sorted(cr_list, key=lambda k: k['label'])


@view_config(context=zeit.content.article.interfaces.IArticle,
             name='seite',
             path_info='.*seite-(.*)',
             renderer='templates/article.html')
class ArticlePage(Article):

    def __call__(self):
        super(ArticlePage, self).__call__()
        self._validate_and_determine_page_nr()

    @zeit.frontend.reify
    def page_nr(self):
        return self._validate_and_determine_page_nr()

    def _validate_and_determine_page_nr(self):
        try:
            spec = self.request.path_info.split('/')[-1][6:]
            number = int(re.sub('[^0-9]', '', spec))
        except (AssertionError, IndexError, ValueError):
            raise pyramid.httpexceptions.HTTPMovedPermanently(
                self.resource_url)
        else:
            if len(str(number)) != len(spec):
                # Make sure /seite-007 is redirected to /seite-7
                raise pyramid.httpexceptions.HTTPMovedPermanently(
                    '%s/%s-%s' % (
                        self.resource_url, self.request.view_name, number))
            elif number > len(self.pages):
                raise pyramid.httpexceptions.HTTPNotFound()
            elif number == 0:
                raise pyramid.httpexceptions.HTTPMovedPermanently(
                    self.resource_url)
            return number

    @zeit.frontend.reify
    def current_page(self):
        return zeit.frontend.interfaces.IPages(self.context)[self.page_nr - 1]

    @zeit.frontend.reify
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

    @zeit.frontend.reify
    def header_img(self):
        obj = self.first_body_obj
        if zeit.content.article.edit.interfaces.IImage.providedBy(obj):
            img = self._create_obj(zeit.frontend.block.HeaderImage, obj)
            if img:
                self._copyrights.setdefault(img.uniqueId, img)
            return img


@view_config(context=zeit.frontend.article.IFeatureLongform,
             renderer='templates/feature_longform.html')
class FeatureLongform(LongformArticle):
    pass


@view_config(context=zeit.frontend.article.IShortformArticle,
             renderer='templates/shortform.html')
class ShortformArticle(Article):
    pass


@view_config(context=zeit.frontend.article.IColumnArticle,
             renderer='templates/column.html')
class ColumnArticle(Article):
    pass


@view_config(context=zeit.frontend.article.IPhotoclusterArticle,
             renderer='templates/photocluster.html')
class PhotoclusterArticle(Article):

    def __init__(self, *args, **kwargs):
        super(PhotoclusterArticle, self).__init__(*args, **kwargs)
        for page in self.pages:
            for index in range(len(page)):
                if issubclass(
                        type(page[index]), zeit.frontend.gallery.Gallery):
                    cls = type('Photocluster',
                               (zeit.frontend.gallery.Gallery,), {})
                    page[index] = cls(page[index].context)


@view_config(name='teaser',
             context=zeit.content.article.interfaces.IArticle,
             renderer='templates/teaser.html')
class Teaser(Article):

    @zeit.frontend.reify
    def teaser_text(self):
        return self.context.teaser
