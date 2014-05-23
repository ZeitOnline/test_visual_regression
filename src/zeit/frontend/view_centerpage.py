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
import zeit.seo

log = logging.getLogger(__name__)


@view_config(context=zeit.content.cp.interfaces.ICenterPage,
             renderer='templates/centerpage.html')
class Centerpage(zeit.frontend.view.Base):

    advertising_enabled = True

    def __call__(self):
        self.context.advertising_enabled = self.advertising_enabled
        stats_path = self.request.registry.settings.node_comment_statistics
        self._unique_id_comments = comments.comments_per_unique_id(stats_path)
        return super(Centerpage, self).__call__()

    def __init__(self, context, request):
        super(Centerpage, self).__init__(context, request)
        try:
            mtb_teaserbar = self.context['teaser-mosaic'].values()[0]
            if mtb_teaserbar.layout.id == 'zmo-mtb':
                self._monothematic_block = mtb_teaserbar
        except IndexError:
            log.error('no monothematic block present')
            self._monothematic_block = None
        try:
            zmo_teaserbar = self.context['teaser-mosaic'].values()[1]
            if zmo_teaserbar.layout.id == 'zmo-teaser-bar':
                self._teaserbar = zmo_teaserbar
        except IndexError:
            log.error('no teaserbar present')
            self._teaserbar = None

    @property
    def monothematic_block(self):
        if self._monothematic_block is not None:
            return self._monothematic_block

    @property
    def teaserbar(self):
        if self._teaserbar is not None:
            return self._teaserbar

    @property
    def type(self):
        return type(self.context).__name__.lower()

    @property
    def is_hp(self):
        if self.request.path == '/' + self.request.registry.settings.hp:
            return True
        else:
            return False

    @property
    def pagetitle(self):
        seo = zeit.seo.interfaces.ISEO(self.context)
        pagetitle = \
            'ZEITmagazin ONLINE - Mode & Design, Essen & Trinken, Leben'
        try:
            if self.context.title:
                pagetitle = self.context.title
        except AttributeError:
            log.error('no title present')
        try:
            if seo.html_title:
                pagetitle = seo.html_title
        except AttributeError:
            log.error('no seo.html_title present')
        return pagetitle

    @property
    def pagetitle_in_body(self):
        return self.context.title

    @property
    def pagedescription(self):
        seo = zeit.seo.interfaces.ISEO(self.context)
        pagedescription = \
            'ZEITmagazin ONLINE - Mode & Design, Essen & Trinken, Leben'
        try:
            if self.context.title:
                pagedescription = self.context.subtitle
        except AttributeError:
            log.error('no subtitle present')
        try:
            if seo.html_title:
                pagedescription = seo.html_description
        except AttributeError:
            log.error('no no seo.html_description present')
        return pagedescription

    @property
    def rankedTags(self):
        return self.context.keywords

    @property
    def rankedTagsList(self):
        if self.rankedTags:
            return ';'.join([rt.label for rt in self.rankedTags])
        else:
            default_tags = [self.context.ressort, self.context.sub_ressort]
            return ';'.join([dt for dt in default_tags if dt])

    @property
    def metaRobots(self):
        seo = zeit.seo.interfaces.ISEO(self.context)
        meta_robots = 'index,follow,noodp,noydir,noarchive'
        try:
            if seo.meta_robots:
                meta_robots = seo.meta_robots
        except AttributeError:
            log.error('no meta_robots present')
        return meta_robots

    @property
    def area_lead(self):
        teaser_list = self.context['lead'].values()
        for teaser in teaser_list:
            try:
                if (teaser.layout.id == 'zmo-leader-fullwidth'
                        or teaser.layout.id == 'zmo-leader-fullwidth-light'):
                    teaser_list.remove(teaser)
            except:
                pass
        return teaser_list

    def teaser_get_commentcount(self, uniqueId):
        try:
            index = '/' + urlparse.urlparse(uniqueId).path[1:]
            count = self._unique_id_comments[index]
            if int(count) >= 5:
                return count
        except KeyError:
            return None

    @property
    def area_lead1(self):
        teaser_list = self.seperator('before', self.area_lead)
        if teaser_list:
            return teaser_list
        else:
            return self.area_lead

    @property
    def area_lead2(self):
        return self.seperator('after', self.area_lead)

    @property
    def area_informatives(self):
        teaser_list = self.context['informatives'].values()
        return teaser_list

    @property
    def area_informatives1(self):
        teaser_list = self.seperator('before', self.area_informatives)
        if teaser_list:
            return teaser_list
        else:
            return self.area_informatives

    @property
    def area_informatives2(self):
        return self.seperator('after', self.area_informatives)

    def seperator(self, position, obj):
        teaser_list = obj
        for teaser in teaser_list:
            try:
                if teaser.cpextra == 'zmo-seperator-for-cps':
                    split = teaser_list.index(teaser)
                    if position == 'before':
                        teaser_list = teaser_list[:split]
                    else:
                        teaser_list = teaser_list[split:]
                        teaser_list.remove(teaser)
                    return teaser_list
            except:
                pass
        return False

    @property
    def area_lead_full_teaser(self):
        for teaser_block in self.context['lead'].values():
            if (teaser_block.layout.id == 'zmo-leader-fullwidth' or
                    teaser_block.layout.id == 'zmo-leader-fullwidth-light'):
                return teaser_block

    @property
    def area_buzz(self):
        stats_path = self.request.registry.settings.node_comment_statistics
        linkreach = self.request.registry.settings.linkreach_host
        reach = LinkReach(stats_path, linkreach)
        try:
            return dict(twitter=reach.fetch_service('twitter', 3),
                        facebook=reach.fetch_service('facebook', 3),
                        comments=reach.fetch_comments(3)
                        )
        except:
            log.error('Cant reach linkreach')

        return dict(twitter=[],
                    facebook=[],
                    comments=[]
                    )

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
