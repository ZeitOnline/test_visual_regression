import lxml.etree
import pyramid.view

import zeit.content.cp.interfaces
import zeit.push.interfaces

import zeit.web.core.view_centerpage
import zeit.web.site.areas.spektrum
import zeit.web.site.view


# XXX This is copy&paste&tweak of zeit.web.site.areas.spektrum.RSSFeed.
# Could we extract common functionality somehow?
class FeedBase(
        zeit.web.core.view_centerpage.Centerpage, zeit.web.site.view.Base):

    social_field = NotImplemented

    def __call__(self):
        super(FeedBase, self).__call__()
        self.request.response.content_type = 'application/rss+xml'
        return lxml.etree.tostring(
            self.build_feed(), pretty_print=True, xml_declaration=True,
            encoding='UTF-8')

    def build_feed(self):
        E = zeit.web.site.areas.spektrum.ElementMaker
        # Convoluted way of creating a namespaced tag, sigh.
        cns = '{%s}encoded' % zeit.web.site.areas.spektrum.CONTENT_NAMESPACE
        ans = '{%s}link' % zeit.web.site.areas.spektrum.ATOM_NAMESPACE
        E_content_encoded = getattr(E, cns)
        root = E.rss(version='2.0')
        channel = E.channel(
            E.title('ZEIT ONLINE SocialFlow'),
            E.link(self.request.route_url('home')),
            E.description(),
            E.language('de-de'),
            E.copyright('Copyright ZEIT ONLINE GmbH. Alle Rechte vorbehalten'),
            getattr(E, ans)(
                href=self.request.url,
                type=self.request.response.content_type)
        )
        root.append(channel)
        # We want all teasers available in the cp, not just the limited amount
        # available in the ICPFeed.
        for content in zeit.content.cp.interfaces.ITeaseredContent(
                self.context):
            content_url = zeit.web.core.template.create_url(content)
            # XXX Since this view will be accessed via newsfeed.zeit.de, we
            # cannot use route_url() as is, since it uses that hostname, which
            # is not the one we want. In non-production environments this
            # unfortunately still generates un-unseful production links.
            content_url = content_url.replace(
                self.request.route_url('home'), 'http://www.zeit.de/', 1)
            last_published_semantic = (
                zeit.web.site.areas.spektrum.last_published_semantic(content))
            item = E.item(
                E.title(content.title),
                E.link(content_url),
                E.description(content.teaserText),
                E.pubDate(zeit.web.site.areas.spektrum.format_rfc822_date(
                    last_published_semantic)),
                E.guid(content.uniqueId, isPermaLink='false'),
            )
            social_value = getattr(
                zeit.push.interfaces.IPushMessages(content), self.social_field)
            if social_value:
                item.append(E_content_encoded(social_value))
            channel.append(item)
        return root


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-socialflow-twitter',
    renderer='string')
class TwitterFeed(FeedBase):

    social_field = 'short_text'


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-socialflow-facebook',
    renderer='string')
class FacebookFeed(FeedBase):

    social_field = 'long_text'
