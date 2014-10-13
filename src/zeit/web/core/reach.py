import json
import urllib
import urllib2

import zeit.cms.interfaces

import zeit.web.core.comments


__all__ = ['LinkReach']


def comment_score(**ctx):
    """Hook function to assign a score by an articles comment count.

    :param ctx: Linkreach._fetch_feed locals context
    :internal:
    """

    stats_path = ctx['self'].stats_path
    stats = zeit.web.core.comments.comments_per_unique_id(stats_path)
    reverse = dict(reversed(i) for i in stats.iteritems())
    return reverse.get(ctx['path'], 0)


def index_score(**ctx):
    """Hook function to assign a score by an articles index.

    :param ctx: Linkreach._fetch_feed locals context
    :internal:
    """

    return len(ctx.get('output', ())) + 1


class LinkReach(object):

    def __init__(self, stats_path, linkreach):
        self.stats_path = stats_path
        self.linkreach = linkreach

    def fetch(self, service, section, limit):
        """Compile a list of popular articles for a specific service.

        :param str service: One of (comments, mostread, mostsend, twitter,
                        facebook, googleplus)
        :param str section: A valid ZEIT ONLINE section as a lowercased string.
        :param int limit: Maximum amount of articles to fetch. Should be < 20.
        :returns: List of zeit.cms.interfaces.ICMSContent objects.
        :raises: ValueError
        """

        if not 0 < limit < 20:
            raise ValueError('Limit must be between 0 and 10.')

        if service in ('comments',):
            postfix = section and '_' + section or ''
            feed = 'most_comments%s.rss' % postfix
            return self._fetch_feed(feed, limit, score_hook=comment_score)

        elif service in ('mostread', 'mostsend'):
            # Translate to unseparated to underscored term so we can maintain
            # a consistent naming in templates.
            service = service.replace('most', 'most_')
            feed = 'new_%s/%s_%s.rss' % (service, service, section or 'all')
            return self._fetch_feed(feed, limit, score_hook=index_score)

        elif service in ('twitter', 'facebook', 'googleplus'):
            return self._fetch_social(service, section, limit)

        else:
            raise ValueError('No service named: ' + service)

    def _fetch_social(self, service, section, limit):
        """Compile a list of articles popular on a social media network.

        :param str service: Service ID, one of (facebook, twitter, googleplus)
        :param int limit: Maximum amount of articles to fetch.
        :rtype: list
        """

        params = urllib.urlencode({'limit': limit, 'section': section})
        url = '%s/zonrank/%s?%s' % (self.linkreach, service, params)
        output = []

        try:
            raw = urllib2.urlopen(url, timeout=5)
            response = json.load(raw)
        except (urllib2.HTTPError, urllib2.URLError, ValueError):
            return output

        for item in response:
            path = item.get('location', '')
            uri = str(zeit.cms.interfaces.ID_NAMESPACE.strip('/') + path)

            try:
                article = zeit.cms.interfaces.ICMSContent(uri)
            except UserWarning:  # TypeError:
                # Ignore item if CMS lookup fails.
                continue

            article.score = item.get('score', 0)

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

        output = []

        try:
            url = 'http://xml.zeit.de/import/feeds/%s' % feed
            feed = zeit.cms.interfaces.ICMSContent(url)
        except TypeError:
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
                article = zeit.cms.interfaces.ICMSContent(uri)
            except TypeError:
                # Ignore item if CMS lookup fails.
                continue

            article.score = score_hook(**locals())

            output.append(article)

        return output

    def get_counts_by_url(self, url):
        """Get share counts for all services for a specific URL."""
        params = urllib.urlencode({'url': url})
        url = '%s/reach?%s' % (self.linkreach, params)
        try:
            response = urllib2.urlopen(url, timeout=5).read()
            return json.loads(response)
        except (urllib2.HTTPError, urllib2.URLError, ValueError):
            return {}
