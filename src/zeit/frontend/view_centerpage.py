from pyramid.view import view_config
from zeit.frontend.reach import LinkReach
import comments
import logging
import urlparse
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
        return 'Lebensart - Mode, Essen und Trinken, '+ \
                'Partnerschaft | ZEIT ONLINE'

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

    @property
    def area_lead(self):
        teaserblock_list = self.context['lead'].values()
        for teaserblock in teaserblock_list:
            if teaserblock.layout.id == 'zmo-leader-fullwidth':
                teaserblock_list.remove(teaserblock)
        return teaserblock_list

    def teaser_get_commentcount(self, uniqueId):
        unique_id_comments = comments.comments_per_unique_id(self)
        try:
            return unique_id_comments['/'+urlparse.urlparse(uniqueId).path[1:]]
        except KeyError:
            return None

    @property
    def area_lead_full_teaser(self):
        for teaser_block in self.context['lead'].values():
            if teaser_block.layout.id == 'zmo-leader-fullwidth':
                return teaser_block

    @property
    def _shares(self):
        reach_url = self.request.registry.settings.linkreach_host
        return LinkReach(reach_url)

    @property
    def global_twitter_shares(self):
        return self._shares.fetch_data('twitter', 20)[:10]

    @property
    def global_facebook_shares(self):
        return self._shares.fetch_data('facebook', 20)[:10]

    @property
    def global_googleplus_shares(self):
        return self._shares.fetch_data('googleplus', 20)[:10]

    @property
    def area_informatives(self):
        teaser_list = self.context['informatives'].values()
        return teaser_list
