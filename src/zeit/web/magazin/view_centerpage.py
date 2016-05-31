from pyramid.view import view_config
import zope.component

import zeit.cms.interfaces
import zeit.connector.connector
import zeit.connector.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zeit.magazin.interfaces
import zeit.seo

import zeit.web.core.article
import zeit.web.core.comments
import zeit.web.core.interfaces
import zeit.web.core.template
import zeit.web.core.view
import zeit.web.core.view_centerpage
import zeit.web.magazin.view


@view_config(context=zeit.content.cp.interfaces.ICP2009,
             custom_predicates=(zeit.web.magazin.view.is_zmo_content,
                                zeit.web.core.view.is_advertorial),
             renderer='templates/advertorial.html')
@view_config(context=zeit.content.cp.interfaces.ICP2009,
             custom_predicates=(zeit.web.magazin.view.is_zmo_content,),
             renderer='templates/centerpage_legacy.html')
class CenterpageLegacy(zeit.web.core.view_centerpage.Centerpage,
                       zeit.web.magazin.view.Base):

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

    @zeit.web.reify
    def monothematic_block(self):
        try:
            mtb_teaserbar = self.context['teaser-mosaic'].values()[0]
            if mtb_teaserbar.layout.id == 'zmo-mtb':
                return mtb_teaserbar
        except IndexError:
            return

    @zeit.web.reify
    def teaserbar(self):
        try:
            zmo_teaserbar = self.context['teaser-mosaic'].values()[1]
            if zmo_teaserbar.layout.id == 'zmo-teaser-bar':
                return zmo_teaserbar
        except IndexError:
            return

    @zeit.web.reify
    def area_lead(self):
        teaser_list = self.context.values()[0]["lead"].values()
        for teaser in teaser_list:
            try:
                if 'zmo-leader-fullwidth' in teaser.layout.id:
                    teaser_list.remove(teaser)
            except AttributeError:
                continue
        return teaser_list

    @zeit.web.reify
    def area_lead_1(self):
        return self.insert_seperator('before', self.area_lead) or (
            self.area_lead)

    @zeit.web.reify
    def area_lead_2(self):
        return self.insert_seperator('after', self.area_lead)

    @zeit.web.reify
    def area_lead_full_teaser(self):
        for teaser_block in self.context.values()[0]["lead"].values():
            try:
                if 'zmo-leader-fullwidth' in teaser_block.layout.id:
                    return teaser_block
            except AttributeError:
                continue

    @zeit.web.reify
    def area_informatives(self):
        return self.context.values()[0]['informatives'].values()

    @zeit.web.reify
    def area_informatives_1(self):
        return self.insert_seperator('before', self.area_informatives) or (
            self.area_informatives)

    @zeit.web.reify
    def area_informatives_2(self):
        return self.insert_seperator('after', self.area_informatives)

    @zeit.web.reify
    def area_buzz(self):
        conn = zope.component.getUtility(zeit.web.core.interfaces.IReach)
        return (
            ('views', conn.get_views(section='zeit-magazin')),
            ('facebook', conn.get_social(
                facet='facebook', section='zeit-magazin')),
            ('comments', conn.get_comments(section='zeit-magazin')))

    @zeit.web.reify
    def is_advertorial(self):
        return zeit.web.core.view.is_advertorial(self.context, self.request)


@view_config(context=zeit.content.cp.interfaces.ICP2015,
             custom_predicates=(zeit.web.magazin.view.is_zmo_content,
                                zeit.web.core.view.is_advertorial),
             renderer='templates/advertorial.html')
@view_config(context=zeit.content.cp.interfaces.ICP2015,
             custom_predicates=(zeit.web.magazin.view.is_zmo_content,),
             renderer='templates/centerpage.html')
class Centerpage(zeit.web.core.view_centerpage.Centerpage,
                 zeit.web.magazin.view.Base):

    @zeit.web.reify
    def is_hp(self):
        return self.context.type == 'ZMO'
