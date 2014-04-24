from pyramid.view import view_config
from zeit.frontend.reach import LinkReach
import logging
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
        # ToDo(T.B.) should be, doesn't work
        # return self.context.html-meta-title
        return 'Lebensart - Mode, Essen und Trinken, Partnerschaft | ZEIT ONLINE'

    @property
    def pagedescription(self):
        # ToDo(T.B.) should be self.context.html-meta-title, doesn't work
        # return self.context.html-meta-title
        output = 'Die Lust am Leben: Aktuelle Berichte, Ratgeber und...'
        return output

    @property
    def rankedTags(self):
        # ToDo(T.B.) keywords are empty
        return self.context.keywords

    @property
    def rankedTagsList(self):
        keyword_list = ''
        if self.rankedTags:
            # ToDo(T.B.) keywords are empty
            for keyword in self.context.keywords:
                keyword_list += keyword.label + ';'
            return keyword_list[:-1]
        else:
            return 'ZEIT ONLINE, ZEIT MAGAZIN'

    @property
    def area_lead(self):
        teaser_list = self.context['lead'].values()
        for teaser in teaser_list:
            if teaser.layout.id == 'zmo-leader-fullwidth':
                teaser_list.remove(teaser)
        return teaser_list

    @property
    def area_lead_full_teaser(self):
        for teaser_block in self.context['lead'].values():
            if teaser_block.layout.id == 'zmo-leader-fullwidth':
                return teaser_block

    @property
    def area_buzz(self):
        community = self.request.registry.settings.community_host
        linkreach = self.request.registry.settings.linkreach_host
        reach = LinkReach(community, linkreach)
        buzz = dict(twitter=reach.fetch_service('twitter', 3),
                    facebook=reach.fetch_service('facebook', 3),
                    comments=reach.fetch_comments(3)
                    )
        return buzz
