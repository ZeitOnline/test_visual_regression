# -*- coding: utf-8 -*-
import logging

import grokcore.component
import lxml.etree
import pyramid.httpexceptions
import zope.component
import zope.component.interfaces
import zope.interface

import zeit.cms.interfaces
import zeit.content.cp.area
import zeit.content.cp.interfaces

from zeit.web.core.centerpage import Region, Area
import zeit.web
import zeit.web.core.centerpage
import zeit.web.core.interfaces
import zeit.web.core.navigation
import zeit.web.core.template
import zeit.web.core.utils
import zeit.web.core.view
import zeit.web.core.centerpage
import zeit.web.core.view_centerpage
import zeit.web.site.module.buzzbox
import zeit.web.site.module.printbox
import zeit.web.site.view


log = logging.getLogger(__name__)


@zeit.web.view_defaults(
    context=zeit.content.cp.interfaces.ICP2015,
    vertical='zon')
@zeit.web.view_config(
    custom_predicates=(zeit.web.core.view.is_advertorial,),
    renderer='templates/centerpage_advertorial.html')
@zeit.web.view_config(
    renderer='templates/centerpage.html')
class Centerpage(
        zeit.web.core.view_centerpage.Centerpage, zeit.web.site.view.Base):
    """Main view class for ZEIT ONLINE centerpages."""

    def __init__(self, context, request):
        super(Centerpage, self).__init__(context, request)
        self._buzzboard_images = {}

    @zeit.web.reify
    def ressort(self):
        return 'homepage' if self.is_hp else super(Centerpage, self).ressort

    @zeit.web.reify
    def is_ressortpage(self):
        navi = zeit.web.core.navigation.NAVIGATION_SOURCE.navigation
        return any([self.ressort in n for n in navi])

    def buzzboard_images(self, image=None):
        # The list we return shall not include the current image but still be
        # added to the registered images.
        registered_images = self._buzzboard_images.copy()
        if image is not None and image not in self._buzzboard_images.keys():
            self._buzzboard_images.update({image: True})
        return registered_images

    @zeit.web.reify
    def include_optimize(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        if self.is_hp:
            return conf.get('optimize_on_zon_homepage', None)
        else:
            return conf.get('optimize_on_zon_centerpage', None)


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICP2015,
    vertical='zon',
    custom_predicates=(zeit.web.core.view.is_paginated,),
    renderer='templates/centerpage.html')
class CenterpagePage(zeit.web.core.view_centerpage.CenterpagePage, Centerpage):
    pass


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICP2015,
    vertical='zon',
    custom_predicates=(zeit.web.core.view.is_paywalled,))
def temporary_redirect_paywalled_centerpage(context, request):
    """ Centerpages with a paywall actually don't really exist.
    However, a Centerpage which is based on the newest volume object
    (which is called 'Ausgabenseite') is supposed to send a temporary
    redirect, if there's no active subscription.
    Therefore this Centerpage will be the only one with the status
    'paid' for now and therefore uses the paywall logic. (RD, 2016-12-08) """
    raise pyramid.httpexceptions.HTTPTemporaryRedirect(
        location=request.registry.settings['redirect_volume_cp'])


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.IArea,
    vertical='*',  # only works if context provides ICMSContent
    renderer='templates/inc/area/includer.html')
class CenterpageArea(Centerpage):

    has_solo_leader = False

    def __init__(self, context, request):
        # Change context to the CP, so the superclass view properties work.
        super(CenterpageArea, self).__init__(
            zeit.content.cp.interfaces.ICenterPage(context), request)
        self.area = context

    def __call__(self):
        super(CenterpageArea, self).__call__()
        self.request.response.headers.add('X-Robots-Tag', 'noindex')
        return {
            # pyramid's rendering is independent of view class instantiation,
            # and thus is unaffected by our change of self.context.
            'context': self.context,
            'area': self.area,
            'region_loop': {'index': 1}
        }


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.IStoryStream,
    vertical='zon',
    renderer='templates/storystream.html')
class Storystream(Centerpage):
    """Main view class for ZEIT ONLINE storystreams."""

    atom_meta = {
        'count': None,
        'oldest_date': None,
        'latest_date': None
    }

    countable_atom_types = [zeit.content.cp.interfaces.ITeaserBlock]

    def __init__(self, context, request):
        super(Centerpage, self).__init__(context, request)
        self.prepare_atom_meta()

    def prepare_atom_meta(self):

        atom_counter = 0
        oldest_atom = None
        latest_atom = None

        regions = self.regions
        for region in regions:
            areas = region.values()
            for area in areas:
                for module in area.filter_values(*self.countable_atom_types):
                    atom_counter += 1

                    # OPTIMIZE: this traversal is redundant (also done inside
                    # the template). Maybe we should store the teaser
                    # object into the module?
                    teaser = zeit.web.core.template.first_child(module)
                    if ((oldest_atom is None) or
                            (teaser and teaser.tldr_date is not None and
                                oldest_atom > teaser.tldr_date)):
                        oldest_atom = teaser.tldr_date

                    if ((latest_atom is None) or
                            (teaser and teaser.tldr_date is not None and
                                latest_atom < teaser.tldr_date)):
                        latest_atom = teaser.tldr_date

        self.atom_meta['count'] = atom_counter
        self.atom_meta['oldest_date'] = oldest_atom
        self.atom_meta['latest_date'] = latest_atom


@zeit.web.view_defaults(
    context=zeit.content.cp.interfaces.ICenterPage,
    vertical='zon')
@zeit.web.view_config(
    custom_predicates=(zeit.web.core.view.is_advertorial,),
    renderer='templates/centerpage_advertorial.html')
@zeit.web.view_config(
    renderer='templates/centerpage.html')
class LegacyCenterpage(Centerpage):
    """Legacy view for centerpages built with the old cp-editor."""

    @zeit.web.reify
    def regions(self):
        regions = []

        if(len(self.area_solo.values()) > 0):
            region_fullwidth = Region([self.area_solo])
            regions.append(region_fullwidth)

        region_multi = Region([self.area_major, self.area_minor], kind='duo')
        regions.append(region_multi)

        regions += self.region_list_parquet

        return regions

    @zeit.web.reify
    def area_solo(self):
        """Return all fullwidth teaser blocks with a minimum length of 1."""

        def valid_module(m):
            return zeit.web.core.template.get_layout(m) in (
                'zon-fullwidth')

        area = self.context.values()[0]['lead']
        return Area([m for m in area.itervalues() if valid_module(m)])

    @zeit.web.reify
    def area_major(self):
        """Return all non-fullwidth teaser blocks with a min length of 1."""

        def valid_module(m):
            return zeit.web.core.template.get_layout(m) not in (
                'zon-fullwidth', 'hide')

        area = self.context.values()[0]['lead']
        return Area([m for m in area.itervalues() if valid_module(m)],
                    kind='major')

    @zeit.web.reify
    def area_minor(self):
        """Return an automated informatives-style area with buzz and ads."""

        return Area([m for m in (
            self.module_buzz_mostread, self.module_printbox) if m],
            kind='minor')

    @zeit.web.reify
    def module_buzz_mostread(self):
        """Return buzz box module with the top 3 most read articles."""

        return zeit.content.cp.blocks.cpextra.CPExtraBlock(
            self.context,
            lxml.etree.fromstring('<container module="mostread"/>'))

    @zeit.web.reify
    def module_printbox(self):
        """Return the module block for the Printbox or Angebotsbox."""

        return zeit.content.cp.blocks.cpextra.CPExtraBlock(
            self.context,
            lxml.etree.fromstring('<container module="printbox"/>'))

    @zeit.web.reify
    def region_list_parquet(self):
        """Re-model the parquet to conform with new RAM-style structure."""

        regions = []
        for area in self.context.values()[1].itervalues():
            if area.kind != 'parquet':
                continue
            for block in area.values():
                try:
                    legacy = zope.component.getMultiAdapter(
                        (area, block),
                        zeit.content.cp.interfaces.IRenderedArea)
                except (zope.component.interfaces.ComponentLookupError,
                        AttributeError, TypeError):
                    continue
                regions.append(Region([legacy], kind='parquet'))

        return regions


@grokcore.component.adapter(
    zeit.content.cp.interfaces.IArea,
    zeit.content.cp.interfaces.ITeaserBlock)
@grokcore.component.implementer(
    zeit.content.cp.interfaces.IRenderedArea)
class RenderedLegacyArea(zeit.web.core.centerpage.Area):

    def __init__(self, area, block):
        area.count = int(block.xml.get('display_amount', 3))
        uid = unicode(block.xml.find('./referenced_cp'))
        area.referenced_cp = zeit.cms.interfaces.ICMSContent(uid, None)
        area.automatic_type = 'centerpage'
        area.hide_dupes = (block.xml.get('hide-dupes') == 'True')
        auto = zeit.content.cp.interfaces.IRenderedArea(area)
        content = auto._content_query()

        lids = [block.layout.id] + area.count * ['zon-small']
        modules = [zeit.web.core.centerpage.TeaserModule(
            [t], layout=lids.pop(0), parent=self) for t in content]
        super(RenderedLegacyArea, self).__init__(
            modules, kind='parquet', is_teaserbar=True)

        self.read_more = block.read_more
        self.read_more_url = block.read_more_url
        self.title = block.title
        self.referenced_cp = area.referenced_cp
