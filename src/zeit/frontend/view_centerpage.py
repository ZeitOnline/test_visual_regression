from babel.dates import get_timezone
from datetime import date
from pyramid.renderers import render_to_response
from pyramid.response import Response
from pyramid.view import notfound_view_config
from pyramid.view import view_config
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.article.edit.interfaces import IImage
from zeit.content.article.edit.interfaces import IVideo
from zeit.content.image.interfaces import IImageMetadata
from zeit.frontend.log import access_log
from zeit.magazin.interfaces import IArticleTemplateSettings, INextRead
from zope.component import providedBy
import logging
import os.path
import pyramid.response
import zeit.connector.connector
import zeit.connector.interfaces
import zeit.content.cp.interfaces
import zeit.content.article.interfaces
import zeit.content.image.interfaces
import zeit.frontend.article
import zeit.frontend.view

log = logging.getLogger(__name__)


@view_config(context=zeit.content.cp.interfaces.ICenterPage,
             renderer='templates/centerpage.html')
class Centerpage(zeit.frontend.view.Base):

    @property
    def pagetitle(self):
        #ToDo(T.B.) should be, doesn't work
        #return self.context.html-meta-title
        return 'Lebensart - Mode, Essen und Trinken, Partnerschaft | ZEIT ONLINE'

    @property
    def pagedescription(self):
        #ToDo(T.B.) should be self.context.html-meta-title, doesn't work
        #return self.context.html-meta-title
        output = 'Die Lust am Leben: Aktuelle Berichte, Ratgeber und...'
        return output

    @property
    def rankedTags(self):
        #ToDo(T.B.) keywords are empty
        return self.context.keywords

    @property
    def rankedTagsList(self):
        keyword_list = ''
        if self.rankedTags:
            #ToDo(T.B.) keywords are empty
            for keyword in self.context.keywords:
                keyword_list += keyword.label + ';'
            return keyword_list[:-1]
        else:
            return 'ZEIT ONLINE, ZEIT MAGAZIN'
