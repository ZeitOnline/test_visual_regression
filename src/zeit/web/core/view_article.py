import datetime
import itertools
import logging
import re

from pyramid.view import view_config
import pyramid.httpexceptions
import zope.component

import zeit.content.article.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.author.interfaces
import zeit.magazin.interfaces

import zeit.web
import zeit.web.core.article
import zeit.web.core.interfaces
import zeit.web.core.template
import zeit.web.core.view
import zeit.web.magazin.view


log = logging.getLogger(__name__)


class Article(zeit.web.core.view.Content):

    advertising_enabled = True
    is_longform = False
    main_nav_full_width = False
    page_nr = 1

    def __init__(self, *args, **kwargs):
        super(Article, self).__init__(*args, **kwargs)
        self._copyrights = {}
        self.context.advertising_enabled = self.banner_on
        self.context.main_nav_full_width = self.main_nav_full_width
        self.context.is_longform = self.is_longform
        self.context.current_year = datetime.date.today().year
        # throw 404 for 'komplettansicht' if there's just one article page
        if self.is_all_pages_view and len(self.pages) == 1:
            raise pyramid.httpexceptions.HTTPNotFound()

    @zeit.web.reify
    def main_image_block(self):
        img = zeit.web.core.interfaces.IFrontendBlock(
            self.context.main_image_block, None)
        if img is not None:
            img.itemprop = 'image'
        try:
            self._copyrights.setdefault(img.uniqueId, img)
        except AttributeError:
            pass
        return img

    @zeit.web.reify
    def template(self):
        return self.context.template or 'default'

    @zeit.web.reify
    def header_layout(self):
        return self.context.header_layout or 'default'

    @zeit.web.reify
    def pages(self):
        return zeit.web.core.interfaces.IPages(self.context)

    @zeit.web.reify
    def is_all_pages_view(self):
        return self.request.view_name == 'komplettansicht'

    @zeit.web.reify
    def current_page(self):
        return self.pages[0]

    @zeit.web.reify
    def next_title(self):
        if self.page_nr < len(self.pages):
            return self.pages[self.page_nr].teaser

    @zeit.web.reify
    def pages_titles(self):
        titles = []
        for number in range(0, len(self.pages)):
            title = self.title
            if number > 0:
                title = self.pages[number].teaser
            titles.append(title)
        return titles

    @zeit.web.reify
    def pages_urls(self):
        urls = []
        for number in range(0, len(self.pages)):
            url = self.content_url
            if number > 0:
                url += '/seite-' + str(number + 1)
            urls.append(url)
        return urls

    @zeit.web.reify
    def next_page_url(self):
        if self.is_all_pages_view:
            return None
        actual_index = self.page_nr - 1
        return self.pages_urls[actual_index + 1] \
            if actual_index + 1 < len(self.pages) else None

    @zeit.web.reify
    def prev_page_url(self):
        actual_index = self.page_nr - 1
        return self.pages_urls[actual_index - 1] \
            if actual_index - 1 >= 0 else None

    @zeit.web.reify
    def pagination(self):
        current = self.page_nr
        total = len(self.pages)
        pager = zeit.web.core.template.calculate_pagination(current, total)

        return {
            'current': current,
            'total': total,
            'pager': pager,
            'next_page_title': self.next_title,
            'content_url': self.content_url,
            'pages_titles': self.pages_titles,
            'pages_urls': self.pages_urls,
            'next_page_url': self.next_page_url,
            'prev_page_url': self.prev_page_url
        }

    @zeit.web.reify
    def syndication_source(self):
        if self.context.product and self.context.product.id == 'TGS':
            return 'http://www.tagesspiegel.de'
        elif self.context.product and self.context.product.id == 'HaBl':
            return 'http://www.handelsblatt.com'
        else:
            return

    @zeit.web.reify
    def first_body_obj(self):
        body = zeit.content.article.edit.interfaces.IEditableBody(self.context)
        return body.values().pop(0) if len(body.values()) > 0 else None

    def _create_obj(self, _cls, obj):
        try:
            return _cls(obj)
        except OSError:
            log.debug('Object does not exist.')

    @zeit.web.reify
    def header_img(self):
        obj = self.first_body_obj
        if zeit.content.article.edit.interfaces.IImage.providedBy(obj):
            img = zeit.web.core.block.HeaderImageStandard(obj)
            if img:
                try:
                    self._copyrights.setdefault(img.uniqueId, img)
                except AttributeError:
                    pass
            return img

    @zeit.web.reify
    def header_video(self):
        obj = self.first_body_obj
        if zeit.content.article.edit.interfaces.IVideo.providedBy(obj):
            return self._create_obj(zeit.web.core.block.HeaderVideo, obj)

    @zeit.web.reify
    def first_img(self):
        obj = self.first_body_obj
        if zeit.content.article.edit.interfaces.IImage.providedBy(obj):
            return self._create_obj(zeit.web.core.block.Image, obj)

    @zeit.web.reify
    def header_elem(self):
        return self.header_video or self.header_img

    @zeit.web.reify
    def resource_url(self):
        return self.request.resource_url(self.context).rstrip('/')

    @zeit.web.reify
    def authors(self):
        return zeit.web.core.article.convert_authors(
            self.context, self.is_longform)

    @zeit.web.reify
    def authors_list(self):
        if self.authors:
            return u';'.join([
                rt['name'] for rt in self.authors if rt.get('name')])

    @zeit.web.reify
    def linkreach(self):
        reach = zope.component.getUtility(zeit.web.core.interfaces.IReach)
        return reach.get_buzz(self.context.uniqueId).get('social')

    @zeit.web.reify
    def tracking_type(self):
        return self.type

    @zeit.web.reify
    def text_length(self):
        return self.context.textLength

    @zeit.web.reify
    def news_source(self):
        """1:1 implementation of questionable xslt construct"""

        if (self.context.ressort == 'News' and
                self.context.product and self.context.product.id == 'News'):
            return 'dpa'
        elif self.context.product and self.context.product.id == 'SID':
            return 'Sport-Informations-Dienst'
        else:
            try:
                return self.context.copyrights.replace(
                    ',', ';').replace(' ', '')
            except(AttributeError):
                return ""

    @zeit.web.reify
    def is_breaking(self):
        return zeit.content.article.interfaces.IBreakingNews(
            self.context).is_breaking

    @zeit.web.reify
    def is_push_news(self):
        return self.context.push_news

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
                        image=zeit.web.core.template.create_url(
                            None, i.src, self.request),
                        link=i.copyright[0][1],
                        nofollow=i.copyright[0][2]
                    )
                )
        return sorted(cr_list, key=lambda k: k['label'])


@view_config(custom_predicates=(zeit.web.core.is_admin,),
             context=zeit.content.article.interfaces.IArticle,
             route_name='instantarticle',
             renderer='templates/instantarticle.html')
class InstantArticle(Article):
    pass


class ArticlePage(Article):

    def __call__(self):
        self._validate_and_determine_page_nr()
        super(ArticlePage, self).__call__()
        return {}

    @zeit.web.reify
    def page_nr(self):
        return self._validate_and_determine_page_nr()

    def _validate_and_determine_page_nr(self):
        # see https://github.com/ZeitOnline/zeit.web/wiki/Artikel#seo
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
            elif number == 1 or number == 0:
                raise pyramid.httpexceptions.HTTPMovedPermanently(
                    self.resource_url)
            return number

    @zeit.web.reify
    def current_page(self):
        return self.pages[self.page_nr - 1]

    @zeit.web.reify
    def next_title(self):
        if self.page_nr < len(self.pages):
            return self.pages[self.page_nr].teaser
