import lxml.etree
from pyramid.decorator import reify
from pyramid.view import view_config

import zeit.cms.interfaces
import zeit.connector.connector
import zeit.connector.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zeit.seo

import zeit.web.core.article
import zeit.web.core.comments
import zeit.web.core.interfaces
import zeit.web.core.reach
import zeit.web.core.template
import zeit.web.core.view


def register_copyrights(func):
    """A decorator that registers all teaser image copyrights it finds in the
    teaser container the decorated method (or property) returns.
    """
    def wrapped(self):
        container = func(self)
        if container:
            for t in zeit.web.core.interfaces.ITeaserSequence(container):
                if t.image:
                    self._copyrights.setdefault(t.image.image_group, t.image)
        return container
    return wrapped


@view_config(context=zeit.content.cp.interfaces.ICenterPage,
             renderer='templates/centerpage.html')
class Centerpage(zeit.web.core.view.Base):

    advertising_enabled = True

    def __init__(self, *args, **kwargs):
        super(Centerpage, self).__init__(*args, **kwargs)
        self._copyrights = {}
        self.context.advertising_enabled = self.advertising_enabled

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

    @reify
    def is_hp(self):
        return self.request.path == '/' + self.request.registry.settings.hp

    @reify
    def meta_robots(self):
        seo = zeit.seo.interfaces.ISEO(self.context)
        try:
            if seo.meta_robots:
                return seo.meta_robots
        except AttributeError:
            pass
        return 'index,follow,noodp,noydir,noarchive'

    @reify
    def tracking_type(self):
        return type(self.context).__name__.title()

    @reify
    @register_copyrights
    def monothematic_block(self):
        try:
            mtb_teaserbar = self.context['teaser-mosaic'].values()[0]
            if mtb_teaserbar.layout.id == 'zmo-mtb':
                return mtb_teaserbar
        except IndexError:
            return

    @reify
    @register_copyrights
    def teaserbar(self):
        try:
            zmo_teaserbar = self.context['teaser-mosaic'].values()[1]
            if zmo_teaserbar.layout.id == 'zmo-teaser-bar':
                return zmo_teaserbar
        except IndexError:
            return

    @reify
    def area_lead(self):
        teaser_list = self.context['lead'].values()
        for teaser in teaser_list:
            try:
                if 'zmo-leader-fullwidth' in teaser.layout.id:
                    teaser_list.remove(teaser)
            except AttributeError:
                continue
        return teaser_list

    @reify
    @register_copyrights
    def area_lead_1(self):
        return self.insert_seperator('before', self.area_lead) or \
            self.area_lead

    @reify
    @register_copyrights
    def area_lead_2(self):
        return self.insert_seperator('after', self.area_lead)

    @reify
    @register_copyrights
    def area_lead_full_teaser(self):
        for teaser_block in self.context['lead'].values():
            try:
                if 'zmo-leader-fullwidth' in teaser_block.layout.id:
                    return teaser_block
            except AttributeError:
                continue

    @reify
    def area_informatives(self):
        return self.context['informatives'].values()

    @reify
    @register_copyrights
    def area_informatives_1(self):
        return self.insert_seperator('before', self.area_informatives) or \
            self.area_informatives

    @reify
    @register_copyrights
    def area_informatives_2(self):
        return self.insert_seperator('after', self.area_informatives)

    @reify
    def area_buzz(self):
        stats_path = self.request.registry.settings.node_comment_statistics
        linkreach = self.request.registry.settings.linkreach_host
        reach = zeit.web.core.reach.LinkReach(stats_path, linkreach)
        teaser_dict = {}
        for service in ('twitter', 'facebook', 'comments'):
            teaser_dict[service] = reach.fetch_service(service, 3)
        return teaser_dict

    @reify
    def copyrights(self):
        teaser_list = []
        for teaser in self._copyrights.itervalues():
            if not len(teaser.copyright) or len(teaser.copyright[0][0]) <= 1:
                # Drop teaser if no copyright text is assigned.
                continue
            teaser_list.append(
                dict(
                    label=teaser.copyright[0][0],
                    image=zeit.web.core.template.translate_url(teaser.src),
                    link=teaser.copyright[0][1],
                    nofollow=teaser.copyright[0][2]
                )
            )
        return sorted(teaser_list, key=lambda k: k['label'])


@view_config(context=zeit.content.cp.interfaces.ICenterPage,
             name='xml', renderer='string')
class XMLView(zeit.web.core.view.Base):

    def __call__(self):
        xml = zeit.content.cp.interfaces.IRenderedXML(self.context)
        return lxml.etree.tostring(xml, pretty_print=True)
