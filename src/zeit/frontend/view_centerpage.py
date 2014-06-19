from pyramid.view import view_config
from zeit.frontend.reach import LinkReach
import comments
import logging
import urlparse
import zeit.cms.interfaces
import zeit.connector.connector
import zeit.connector.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zeit.frontend.article
import zeit.frontend.interfaces
import zeit.frontend.template
import zeit.frontend.view
import zeit.seo

log = logging.getLogger(__name__)


def register_copyrights(func):
    # TODO: This decorator does not propagate exceptions.
    def wrapped(self):
        container = func(self)
        if not container:
            return container
        for teaser in zeit.frontend.interfaces.ITeaserSequence(container):
            self._copyrights.setdefault(teaser.image.image_group, teaser.image)
        return container
    return wrapped


@view_config(context=zeit.content.cp.interfaces.ICenterPage,
             renderer='templates/centerpage.html')
class Centerpage(zeit.frontend.view.Base):

    advertising_enabled = True

    def __init__(self, *args, **kwargs):
        super(Centerpage, self).__init__(*args, **kwargs)
        self._copyrights = {}

    def __call__(self):
        self.context.advertising_enabled = self.advertising_enabled
        stats_path = self.request.registry.settings.node_comment_statistics
        self._unique_id_comments = comments.comments_per_unique_id(stats_path)
        return super(Centerpage, self).__call__()

    def insert_seperator(self, position, obj):
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
                continue

    def teaser_get_commentcount(self, uniqueId):
        try:
            index = '/' + urlparse.urlparse(uniqueId).path[1:]
            count = self._unique_id_comments[index]
            if int(count) >= 5:
                return count
        except KeyError:
            return

    @property
    def is_hp(self):
        return self.request.path == '/' + self.request.registry.settings.hp

    @property
    def meta_robots(self):
        seo = zeit.seo.interfaces.ISEO(self.context)
        meta_robots = 'index,follow,noodp,noydir,noarchive'
        try:
            if seo.meta_robots:
                meta_robots = seo.meta_robots
        except AttributeError:
            log.error('no meta_robots present')
        return meta_robots

    @property
    def tracking_type(self):
        return type(self.context).__name__.title()

    @property
    @register_copyrights
    def monothematic_block(self):
        try:
            mtb_teaserbar = self.context['teaser-mosaic'].values()[0]
            if mtb_teaserbar.layout.id == 'zmo-mtb':
                return mtb_teaserbar
        except IndexError:
            return

    @property
    @register_copyrights
    def teaserbar(self):
        try:
            zmo_teaserbar = self.context['teaser-mosaic'].values()[1]
            if zmo_teaserbar.layout.id == 'zmo-teaser-bar':
                return zmo_teaserbar
        except IndexError:
            return

    @property
    def area_lead(self):
        teaser_list = self.context['lead'].values()
        for teaser in teaser_list:
            try:
                if 'zmo-leader-fullwidth' in teaser.layout.id:
                    teaser_list.remove(teaser)
            except AttributeError:
                continue
        return teaser_list

    @property
    @register_copyrights
    def area_lead_1(self):
        return self.insert_seperator('before', self.area_lead) or \
            self.area_lead

    @property
    @register_copyrights
    def area_lead_2(self):
        return self.insert_seperator('after', self.area_lead)

    @property
    @register_copyrights
    def area_lead_full_teaser(self):
        for teaser_block in self.context['lead'].values():
            try:
                if 'zmo-leader-fullwidth' in teaser_block.layout.id:
                    return teaser_block
            except AttributeError:
                continue
        return None

    @property
    def area_informatives(self):
        return self.context['informatives'].values()

    @property
    @register_copyrights
    def area_informatives_1(self):
        return self.insert_seperator('before', self.area_informatives) or \
            self.area_informatives

    @property
    @register_copyrights
    def area_informatives_2(self):
        return self.insert_seperator('after', self.area_informatives)

    @property
    def area_buzz(self):
        stats_path = self.request.registry.settings.node_comment_statistics
        linkreach = self.request.registry.settings.linkreach_host
        reach = LinkReach(stats_path, linkreach)
        teaser_dict = {}
        for service in ('twitter', 'facebook', 'comments'):
            try:
                teaser_list = reach.fetch_service(service, 3)
            except:
                log.error('Can\'t fetch linkreach service %s.' % service)
                teaser_list = []
            teaser_dict[service] = teaser_list
        return teaser_dict

    @property
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
