import pyramid.view
import lxml.etree

import zeit.cms.interfaces
import zeit.cms.workflow
import zeit.content.cp.interfaces

import zeit.web.core.view


class Centerpage(zeit.web.core.view.CeleraOneMixin, zeit.web.core.view.Base):

    advertising_enabled = True

    def __init__(self, *args, **kwargs):
        super(Centerpage, self).__init__(*args, **kwargs)
        self.context.advertising_enabled = self.banner_on

        # Most of our resources will be purged from now on. We test this new
        # mechanism on CPs. This might be valid for all resources in the future
        # (RD, 7.8.2015)
        self.request.response.headers.add('s-maxage', '21600')

    @zeit.web.reify
    def regions(self):
        """List of regions, the outermost container making up our centerpage.
        :rtype: list
        """
        return [zeit.web.core.centerpage.IRendered(x)
                for x in self.context.values()]

    def __iter__(self):
        for region in self.regions:
            for area in region.values():
                for teaser in zeit.content.cp.interfaces.ITeaseredContent(
                        area):
                    if zeit.web.core.view.known_content(teaser):
                        yield teaser

    @zeit.web.reify
    def canonical_url(self):
        url = super(Centerpage, self).canonical_url.replace(
            'index.cp2015', 'index')  # XXX: remove soon (aps)
        page = self.request.params.get('p', None)
        param_str = '?p=' + page if page and page != '1' else ''
        return url + param_str

    @zeit.web.reify
    def is_hp(self):
        return self.context.type == 'homepage'

    @zeit.web.reify
    def has_solo_leader(self):
        try:
            return self.regions[0].values()[0].kind == 'solo'
        except (AttributeError, IndexError):
            return False

    @zeit.web.reify
    def meta_robots(self):
        # Prevent continuation pages from being indexed
        if zeit.web.core.view.is_paginated(self.context, self.request):
            return 'noindex,follow,noodp,noydir,noarchive'
        return super(Centerpage, self).meta_robots

    @zeit.web.reify
    def tracking_type(self):
        return type(self.context).__name__.title()

    @zeit.web.reify
    def comment_counts(self):
        return zeit.web.core.comments.get_counts(*[t.uniqueId for t in self])

    @zeit.web.reify
    def has_cardstack(self):
        kwargs = {'cp:type': 'cardstack'}
        return bool(zeit.web.core.utils.find_block(self.context, **kwargs))


@pyramid.view.view_config(
    route_name='json_update_time',
    renderer='jsonp')
def json_update_time(request):
    try:
        resource = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/{}'.format(
                request.matchdict['path']), None)
        if resource is None:
            resource = zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/{}'.format(request.matchdict['path']))

        info = zeit.cms.workflow.interfaces.IPublishInfo(resource)
        dlps = info.date_last_published_semantic.isoformat()
        dlp = info.date_last_published.isoformat()

    except (AttributeError, KeyError, TypeError):
        dlps = dlp = None
    request.response.cache_expires(5)
    return {'last_published': dlp, 'last_published_semantic': dlps}


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='xml',
    renderer='string')
class XMLView(zeit.web.core.view.Base):

    def __call__(self):
        xml = zeit.content.cp.interfaces.IRenderedXML(self.context)
        return lxml.etree.tostring(xml, pretty_print=True)
