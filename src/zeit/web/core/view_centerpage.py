import collections
import copy

import pyramid.view
import lxml.etree

import zeit.cms.interfaces
import zeit.cms.workflow
import zeit.content.cp.interfaces

import zeit.web.core.view


class Centerpage(zeit.web.core.view.Base):

    advertising_enabled = True

    def __init__(self, *args, **kwargs):
        super(Centerpage, self).__init__(*args, **kwargs)
        self._copyrights = {}
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
    def is_hp(self):
        return self.context.type == 'homepage'

    @zeit.web.reify
    def has_solo_leader(self):
        try:
            return self.regions[0].values()[0].kind == 'solo'
        except (AttributeError, IndexError):
            return False

    @zeit.web.reify
    def tracking_type(self):
        return type(self.context).__name__.title()

    @zeit.web.reify
    def comment_counts(self):
        return zeit.web.core.comments.get_counts(*[t.uniqueId for t in self])


@pyramid.view.view_config(
    route_name='json_update_time',
    renderer='jsonp')
def json_update_time(request):
    try:
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
    context=zeit.content.cp.interfaces.ICP2009,
    name='xml',
    renderer='string')
class LegacyXMLView(zeit.web.core.view.Base):

    def __call__(self):
        xml = zeit.content.cp.interfaces.IRenderedXML(self.context)
        return lxml.etree.tostring(xml, pretty_print=True)


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICP2015,
    name='xml',
    renderer='string')
class XMLView(zeit.web.core.view.Base):

    def __call__(self):
        nsmap = collections.OrderedDict((
            ('cp', 'http://namespaces.zeit.de/CMS/cp'),
            ('py', 'http://codespeak.net/lxml/objectify/pytype'),
            ('xi', 'http://www.w3.org/2001/XInclude'),
            ('xsd', 'http://www.w3.org/2001/XMLSchema'),
            ('xsi', 'http://www.w3.org/2001/XMLSchema-instance'),
        ))
        maker = lxml.objectify.ElementMaker(nsmap=nsmap)
        root = getattr(maker, self.context.xml.tag)(
            **self.context.xml.attrib)
        root.append(copy.copy(self.context.xml.head))
        body = lxml.objectify.E.body()
        root.append(body)
        for region in self.context.body.values():
            body.append(zeit.content.cp.interfaces.IRenderedXML(region))
        return lxml.etree.tostring(root, pretty_print=True)
