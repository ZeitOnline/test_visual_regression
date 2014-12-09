import json
import urllib
import urllib2

import zope.component

import zeit.cms.interfaces

import zeit.web
import zeit.web.core.application
import zeit.web.core.comments
import zeit.web.core.utils


__all__ = ['fetch']


def comment_score(**ctx):
    """Hook function to assign a score by an articles comment count.

    :param ctx: Linkreach._fetch_feed locals context
    :internal:
    """

    comments = zeit.web.core.comments.comments_per_unique_id()
    return int(comments.get(ctx.get('path'), 0))


def index_score(**ctx):
    """Hook function to assign a score by an articles index.

    :param ctx: Linkreach._fetch_feed locals context
    :internal:
    """

    return len(ctx.get('output', ())) + 1


class Fetcher(object):

    @zeit.web.reify
    def _linkreach_host(self):
        zwcs = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        return zeit.web.core.application.maybe_convert_egg_url(
            zwcs.get('linkreach_host', ''))

    def __call__(self, service, target, limit=3):
        """Compile a list of popular articles for a specific service.

        :param str service: One of (comments, mostread, mostsend, twitter,
                        facebook, googleplus, path)
        :param str target: A valid ZEIT ONLINE section as a lowercased string
                           or content path (if service equals `path`)
        :param int limit: Maximum amount of articles to fetch. Should be < 20.
        :returns: List of zeit.cms.interfaces.ICMSContent objects.
        :raises: ValueError
        """

        if isinstance(target, basestring):
            target = target.lower()
        else:
            raise TypeError('Buzz target must be a string.')

        if not 0 < limit < 20:
            raise ValueError('Limit must be between 0 and 10.')

        if service in ('path',):
            return self._fetch_path(target)

        elif service in ('comments',):
            postfix = target and '_' + target or ''
            feed = 'most_comments%s.rss' % postfix
            return self._fetch_feed(feed, limit, score_hook=comment_score)

        elif service in ('mostread', 'mostsend'):
            # Translate unseparated to underscored term, so we can maintain
            # a consistent naming scheme in our templates.
            service = service.replace('most', 'most_')
            feed = 'new_%s/%s_%s.rss' % (service, service, target or 'all')
            return self._fetch_feed(feed, limit, score_hook=index_score)

        elif service in ('twitter', 'facebook', 'googleplus'):
            return self._fetch_social(service, target, limit)

        else:
            raise ValueError('No service named: ' + service)

    def _fetch_social(self, service, section, limit):
        """Compile a list of articles popular on a social media network.

        :param str service: Service ID, one of (facebook, twitter, googleplus)
        :param int limit: Maximum amount of articles to fetch.
        :rtype: list
        """

        params = urllib.urlencode({'limit': limit, 'section': section})
        url = '%s/zonrank/%s?%s' % (self._linkreach_host, service, params)

        output = zeit.web.core.utils.nslist()

        try:
            raw = urllib2.urlopen(url, timeout=5)
            response = json.load(raw)
        except (urllib2.HTTPError, urllib2.URLError, ValueError):
            return output

        for item in response:
            uri = 'http://xml.zeit.de' + item.get('location', '')

            try:
                content = zeit.cms.interfaces.ICMSContent(uri)
            except TypeError:
                # Ignore item if CMS lookup fails.
                continue

            article = {
                'teaserSupertitle': content.teaserSupertitle,
                'teaserTitle': content.teaserTitle,
                'uniqueId': content.uniqueId,
                'score': item.get('score', 0)
            }

            output.append(article)

        return output

    def _fetch_feed(self, feed, limit, score_hook=lambda **ctx: 0):
        """Compile a list of articles from an RSS feed.

        :param str feed: Name of feed located in {DAV}/import/feeds/
        :param int limit: Maximum amount of articles to fetch.
        :param score_hook: Callable to provide article score. Should accept
                           context keyword args.
        :rtype: list
        """

        output = zeit.web.core.utils.nslist()

        try:
            url = 'http://xml.zeit.de/import/feeds/%s' % feed
            feed = zeit.cms.interfaces.ICMSContent(url)
            # XXX: If feed is a zeit.cms.repository.interfaces.IUnknownResource
            #      it breaks the ICMSContent interface!
            assert hasattr(feed, 'xml')
        except (AssertionError, TypeError):
            # Return empty-handed if feed is unavailable.
            return output

        iterator = iter(feed.xml.xpath('/rss/channel/item'))

        while len(output) < limit:
            try:
                rss_node = iterator.next()
            except StopIteration:
                # Abort compiling article list if feed is exhausted.
                break

            links = rss_node.xpath('link/text()')
            if not len(links):
                continue
            path = links[0].replace('http://www.zeit.de', '', 1)
            uri = str(zeit.cms.interfaces.ID_NAMESPACE.strip('/') + path)

            try:
                content = zeit.cms.interfaces.ICMSContent(uri)
            except TypeError:
                # Ignore item if CMS lookup fails.
                continue

            article = {
                'teaserSupertitle': content.teaserSupertitle,
                'teaserTitle': content.teaserTitle,
                'uniqueId': content.uniqueId,
                'score': score_hook(**locals())
            }

            output.append(article)

        return output

    def _fetch_path(self, path):
        """Get share counts for all services for a specific content item."""

        params = urllib.urlencode({'url': path})
        url = '%s/reach?%s' % (self._linkreach_host, params)

        output = zeit.web.core.utils.nsdict()

        try:
            response = urllib2.urlopen(url, timeout=5).read()
            output.update(json.loads(response))
        except (urllib2.HTTPError, urllib2.URLError, ValueError):
            pass

        return output

fetch = Fetcher()
