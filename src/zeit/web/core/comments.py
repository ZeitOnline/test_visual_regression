# -*- coding: utf-8 -*-
import collections
import datetime
import logging
import math

from BeautifulSoup import BeautifulSoup
import babel.dates
import lxml.etree
import pytz
import requests
import requests.exceptions
import zope.component

import zeit.cms.interfaces

import zeit.web.core.cache
import zeit.web.core.interfaces
import zeit.web.core.metrics
import zeit.web.core.template


LONG_TERM_CACHE = zeit.web.core.cache.get_region('long_term')
log = logging.getLogger(__name__)


def rewrite_picture_url(url):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    static_host = conf.get('community_static_host').strip('/')
    community_host = conf.get('community_host').strip('/')
    return url.replace(community_host, static_host)


def comment_to_dict(comment):
    """Expects an lxml element representing an agatho comment and returns a
    dict representation.

    :param comment: lxml.etree.Element comment
    :rtype: dict
    """

    # TODO: Avoid repeatedly evaluating xpaths.

    author_name = ''
    if comment.xpath('author/name/text()'):
        author_name = comment.xpath('author/name/text()')[0]

    if comment.xpath('author/@roles'):
        roles = comment.xpath('author/@roles')[0]
        is_author = 'author' in roles
        is_freelancer = 'freelancer' in roles
        roles = roles.split(',')
        try:
            gender = comment.xpath('author/@sex')[0]
        except IndexError:
            gender = 'undefined'

        roles_words = {u'author_weiblich': 'Redaktion',
                       u'author_männlich': 'Redaktion',
                       u'author_undefined': 'Redaktion',
                       u'expert_weiblich': 'Expertin',
                       u'expert_männlich': 'Experte',
                       u'freelancer_undefined': 'Freier Autor',
                       u'freelancer_weiblich': 'Freie Autorin',
                       u'freelancer_männlich': 'Freier Autor'}

        roles = [roles_words['%s_%s' % (role, gender)] for role in roles
                 if '%s_%s' % (role, gender) in roles_words]
    else:
        is_author = False
        is_freelancer = False
        roles = []

    if comment.xpath('author/@picture'):
        picture_url = rewrite_picture_url(
            comment.xpath('author/@picture')[0])
    else:
        picture_url = None

    if comment.xpath('author/@url'):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        profile_url = (conf.get('community_host', '') +
                       comment.xpath('author/@url')[0])

    if comment.xpath('content/text()'):
        content = comment.xpath('content/text()')[0]
    else:
        content = '[fehler]'

    fans = comment.xpath('flagged[@type="leser_empfehlung"]/@userid')

    # We have the drupal behaviour that the subject is partly coypied from the
    # comment itself, if a subject was not set. This leads to a slightly more
    # complex evaluation of the subject in our usecase
    subject = comment.xpath('subject/text()')
    content_stripped = ''.join(BeautifulSoup(content).findAll(text=True))
    if (subject and not subject[0] == '[empty]' and
            not subject[0] == '[...]' and
            not subject[0] == content_stripped[0:len(subject[0])]):
        content = u'<p>{}</p>{}'.format(comment.xpath('subject/text()')[0],
                                        content)

    if comment.xpath('inreply/@to'):
        in_reply = int(comment.xpath('inreply/@to')[0].lstrip('cid-'))
    else:
        in_reply = None

    tz = babel.dates.get_timezone('Europe/Berlin')
    created = comment.xpath('created/text()')

    if created:
        created = datetime.datetime.fromtimestamp(float(created[0]), tz)
    else:
        # legacy code to mimic new "created" timestamp in agatho thread
        # obsolete since https://github.com/ZeitOnline/community/pull/166
        dts = ('date/year/text()', 'date/month/text()', 'date/day/text()',
               'date/hour/text()', 'date/minute/text()')
        utc = babel.dates.get_timezone('UTC')
        created = datetime.datetime(*(int(comment.xpath(d)[0]) for d in dts)
                                    ).replace(tzinfo=utc).astimezone(tz)
        changed = comment.xpath('changed/text()')

        if changed:
            changed = datetime.datetime.fromtimestamp(float(changed[0]), tz)

            if created.replace(second=59) > changed:
                created = created.replace(second=changed.second)

    # TODO: Catch name and cid unavailabilty in element tree.
    return dict(
        uid=comment.xpath('author/@id')[0].lstrip('uid-'),
        in_reply=in_reply,
        img_url=picture_url,
        userprofile_url=profile_url,
        name=author_name,
        created=created,
        text=content,
        role=', '.join(roles),
        fans=','.join(fans),
        cid=int(comment.xpath('./@id')[0].lstrip('cid-')),
        recommendations=len(
            comment.xpath('flagged[@type="leser_empfehlung"]')),
        is_author=is_author,
        is_freelancer=is_freelancer,
        is_reply=bool(in_reply),
        is_promoted=bool(
            len(comment.xpath('flagged[@type="kommentar_empfohlen"]')))
    )


def request_thread(path):
    """Send a GET request to receive an agatho comment thread.

    :param path: Path section of a uniqueId
    :rtype: unicode or None
    """

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    timeout = float(conf.get('community_host_timeout_secs', 0.5))
    uri = '{}/agatho/thread{}'.format(
        conf.get('agatho_host', ''), path.encode('utf-8'))
    try:
        with zeit.web.core.metrics.timer(
                'request_thread.community.reponse_time'):
            response = requests.get(uri, timeout=timeout)
        if response.status_code == 404:
            return
        return response.content if (200 <= response.status_code < 300) else (
            {'request_failed': datetime.datetime.utcnow()})
    except (AttributeError, requests.exceptions.RequestException):
        return {'request_failed': datetime.datetime.utcnow()}


class ThreadNotLoadable(Exception):
    pass


def get_thread(unique_id, sort='asc', page=None, cid=None, invalidate_delta=5):
    """Return a dict representation of the comment thread of the given
    article.

    :param sort: Sort order of comments, desc or asc
    :param page: Pagination value
    :param cid: Comment ID to calculate appropriate pagination
    :rtype: dict or None
    """

    thread = get_cacheable_thread(unique_id)

    if thread is not None and thread.get('request_failed'):
        td = datetime.datetime.utcnow() - thread.get('request_failed')
        if td >= datetime.timedelta(seconds=invalidate_delta):
            zeit.web.core.view_comment.invalidate_comment_thread(unique_id)
            thread = get_cacheable_thread(unique_id)
        if thread is not None and thread.get('request_failed'):
            raise ThreadNotLoadable()

    if thread is None or thread['comment_count'] == 0:
        return

    # We do not want to touch the references of the cached thread
    thread = thread.copy()
    sorted_tree = thread.pop('sorted_tree', {}).values()
    thread['sort'] = sort

    if sort == 'desc':
        sorted_tree.reverse()
    elif sort == 'promoted':
        # Filter comment thread by promotions, retain sort oder
        gen = ([c, []] for c in thread['flattened_comments'] if (
            c['is_promoted'] is True))
        sorted_tree = sorted(gen, None, lambda c: c[0]['is_promoted'], 1)
    elif sort == 'recommended':
        # Sort and filter comment thread by recommendations
        gen = ([c, []] for c in thread['flattened_comments'] if (
            c['recommendations'] > 0))
        sorted_tree = sorted(gen, None, lambda c: c[0]['recommendations'], 1)

    # calculate comment counts, which differ depending on sort
    top_level_comment_count = len(sorted_tree)
    total_comment_count = len(thread['flattened_comments']) if sort in (
        'desc', 'asc') else len(sorted_tree)
    thread['comment_count'] = len(thread['flattened_comments'])

    # calculate number of pages
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    page_size = int(conf.get('comment_page_size', '10'))
    pages = int(math.ceil(float(top_level_comment_count) / float(page_size)))

    # sanitize page value
    if page:
        try:
            page = int(page)
        except ValueError:
            page = 1

        if page < 1 or page > pages:
            page = 1

    # compute page if comment id is supplied, effectively ignoring page param
    if cid is not None:
        comment_index = thread['index']
        try:
            root_index = comment_index[int(cid)]['root_index']
            if sort == 'desc':
                root_index = abs(root_index - top_level_comment_count)
            page = int(math.ceil(float(root_index) / float(page_size)))
        except (ValueError, KeyError):
            pass

    # slice comment tree when there's more than one page
    if page and pages > 1:
        sorted_tree = sorted_tree[(page - 1) * page_size: page * page_size]

    # flatten comment tree
    thread['comments'] = comments = []
    for main_comment in sorted_tree:
        origin = main_comment[0]
        origin['replies'] = []
        comments.append(origin)
        for sub_comment in main_comment[1]:
            origin['replies'].append(sub_comment)

    # display comment count
    thread['headline'] = '{} {}'.format(
        total_comment_count,
        'Kommentar' if total_comment_count == 1 else 'Kommentare')

    # comments ad place
    thread['ad_place'] = int(page_size / 2 + 1)

    # all things pagination
    thread['pages'] = {
        'current': page,
        'total': pages,
        'pager': zeit.web.core.template.calculate_pagination(page, pages)}

    if page and thread['pages']['pager']:
        thread['pages']['title'] = u'Seite {} von {}'.format(
            page, pages)

    return thread


def community_maintenance():
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    unique_id = conf.get('community_maintenance')
    maintenance = _community_maintenance_cache(unique_id)
    return _derive_maintenance_from_schedule(maintenance)


@LONG_TERM_CACHE.cache_on_arguments()
def _community_maintenance_cache(unique_id=None):
    maintenance = {
        'active': False,
        'scheduled': False,
        'begin': None,
        'end': None,
        'text_scheduled': (u'Aufgrund von Wartungsarbeiten sind die '
                           u'Kommentarfunktionen in Kürze vorübergehend '
                           u'nicht verfügbar. Wir bitten um Ihr '
                           u'Verständnis.'),
        'text_active': (u'Aufgrund von Wartungsarbeiten sind die '
                        u'Kommentarfunktionen vorübergehend '
                        u'nicht mehr verfügbar. Wir bitten um Ihr '
                        u'Verständnis.')
    }

    if unique_id:
        xml = zeit.cms.interfaces.ICMSContent(unique_id).xml
        maintenance = _maintenance_from_xml(xml, maintenance)

    return maintenance


def _maintenance_from_xml(xml, maintenance):
    for key in maintenance.keys():
        elem = (xml.findtext(key) or '').strip()
        if elem == '':
            continue

        if not elem or elem.strip() == '':
            elem = maintenance[key]
        if elem and elem.lower() == 'false':
            elem = False
        if elem and elem.lower() == 'true':
            elem = True
        if zeit.web.core.date.parse_date(elem):
            elem = zeit.web.core.date.parse_date(elem)

        maintenance[key] = elem
    return maintenance


def _derive_maintenance_from_schedule(maintenance):
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    override = maintenance['active']
    if maintenance['scheduled'] and maintenance['begin'] and (
            now - maintenance['begin'] >= datetime.timedelta(0)):
        maintenance['active'] = True

    if not override and maintenance['scheduled'] and maintenance['end'] and (
            now - maintenance['end'] >= datetime.timedelta(0)):
        maintenance['active'] = False
    return maintenance


@LONG_TERM_CACHE.cache_on_arguments()
def get_cacheable_thread(unique_id):

    path = unique_id.replace(zeit.cms.interfaces.ID_NAMESPACE, '/', 1)
    thread = request_thread(path)

    if thread is None:
        return

    if isinstance(thread, dict) and thread.get('request_failed'):
        return thread

    try:
        document = lxml.etree.fromstring(thread)
    except (IOError, lxml.etree.XMLSyntaxError):
        return

    try:
        comment_nid = document.xpath('/comments/nid/text()')[0]
        comment_list = document.xpath('//comment')
    except (IndexError, lxml.etree.XMLSyntaxError):
        return

    comment_count = len(comment_list)
    comment_list = list(comment_to_dict(c) for c in comment_list)
    flattened_comments = comment_list[:]
    has_promotion = has_recommendations = False
    for comment in flattened_comments:
        if comment['recommendations'] > 0:
            has_recommendations = True
        if comment['is_promoted'] is True:
            has_promotion = True
        if has_recommendations and has_promotion:
            break
    sorted_tree, index = _sort_comments(comment_list)

    try:
        return dict(
            sorted_tree=sorted_tree,
            flattened_comments=flattened_comments,
            has_recommendations=has_recommendations,
            has_promotion=has_promotion,
            index=index,
            comment_count=comment_count,
            sort='asc',
            nid=comment_nid)
    except (IndexError, AttributeError):
        return


def _sort_comments(comments):

    comments_sorted = collections.OrderedDict()
    root_ancestors = {}
    comment_index = {}

    while comments:
        comment = comments.pop(0)

        if not comment["in_reply"]:
            root_ancestors[comment['cid']] = comment['cid']
            comments_sorted[comment['cid']] = [comment, []]
            root_index = comments_sorted.keys().index(comment['cid']) + 1
            comment['root_index'] = root_index
            comment['shown_num'] = str(root_index)
        else:
            try:
                ancestor = root_ancestors[comment['in_reply']]
                root_ancestors[comment['cid']] = ancestor
                comments_sorted[ancestor][1].append(comment)
                root_index = comments_sorted[ancestor][0]['root_index']
                comment['root_index'] = root_index
                comment['shown_num'] = "{}.{}".format(root_index, len(
                    comments_sorted[ancestor][1]))
            except KeyError:
                log.error("The comment with the cid {} is a reply, but"
                          " no ancestor could be found".format(comment['cid']))
        comment_index[comment['cid']] = comment
    return (comments_sorted, comment_index)


def request_counts(*unique_ids):
    """Send a POST request to receive multiple comment counts for a CP.

    :param unique_ids: List of uniqueIds
    :rtype: unicode or None
    """

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    timeout = float(conf.get('community_host_timeout_secs', 5))
    uri = '{}/agatho/node-comment-statistics'.format(
        conf.get('community_host', '').rstrip('/'))
    try:
        with zeit.web.core.metrics.timer(
                'request_counts.community.reponse_time'):
            response = requests.post(uri, data=[
                ('unique_ids[]', uid) for uid in unique_ids], timeout=timeout)
        return response.ok and response.content or None
    except (AttributeError, requests.exceptions.RequestException):
        return


def get_counts(*unique_ids):
    """Return a dictionary containing comment counts for a select set of
    content resources. If no resources are specified, the most commented
    resources will be used.

    :param unique_ids: List of uniqueIds
    :rtype: dict
    """

    raw = request_counts(*unique_ids)
    if raw is None:
        return {}
    try:
        ascii = raw.encode('ascii', 'xmlcharrefreplace').strip()
        nodes = lxml.etree.fromstring(ascii).xpath('/nodes/node')
        return {zeit.cms.interfaces.ID_NAMESPACE.rstrip('/') + n.attrib['url']:
                n.attrib['comment_count'] for n in nodes}
    except (AttributeError, IndexError, KeyError, lxml.etree.LxmlError):
        return {}


class UserCommentsException(Exception):
    pass


class PagesExhaustedError(UserCommentsException):
    pass


class NoValidComment(UserCommentsException):
    pass


class CommunityNotReachable(UserCommentsException):
    pass


def get_user_comments(author, page=1, rows=6, sort="DESC"):
    """Return a dictionary containing comments for an IAuthor,

    :param author: An objects which implements zeit.content.author.IAuthor
    :param page: A number which represents the page being retrieved
    :param rows: Number of items being displayed per page
    :param sort: String describing sort order.
                 DESC is descending. ASC is ascending
    :rtype: dict
    """

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)

    if not getattr(author, 'email'):
        return
    uri = '{}/agatho/usercommentsxml/{}/{}/{}/{}'.format(
        conf.get('agatho_host', ''), author.email, (page - 1), rows, sort)

    timeout = float(conf.get('community_host_timeout_secs', 5))

    with zeit.web.core.metrics.timer('user_comments.community.response_time'):
        try:
            result = requests.get(uri, timeout=timeout)
        except requests.exceptions.RequestException:
            raise UserCommentsException()
    if not result.ok:
        return

    xml = lxml.etree.fromstring(result.content)

    uid = None
    try:
        uid = int(xml.xpath('/users_comments/uid')[0].text)
    except TypeError:
        pass

    published_total = None
    try:
        published_total = int(xml.xpath(
            '/users_comments/published_total')[0].text)
    except TypeError:
        pass

    comments = {
        'comments': [],
        'uid': uid,
        'published_total': published_total,
        'page': page,
        'rows': rows,
        'sort': sort
    }

    if rows > 0:
        add = 0 if comments['published_total'] % rows == 0 else 1
        comments['page_total'] = (comments['published_total'] / rows) + add
    else:
        comments['page_total'] = 0

    if page > comments['page_total']:
        raise PagesExhaustedError()

    for comment in xml.xpath('/users_comments//item'):
        comments['comments'].append(UserComment(comment))

    return comments


# XXX Right now we need this for comments, which are displayed on author
# pages. We should think about redesigning this and use one comment object
# throughout the whole comment API (RD, 2015-12-07)
class UserComment(object):
    zope.interface.implements(zeit.cms.interfaces.ICMSContent)

    def __init__(self, comment):
        self._comment = comment
        try:
            int(self._comment.xpath('cid')[0].text)
        except (TypeError, ValueError, IndexError):
            raise NoValidComment('Comment ID (cid) must be given.')

    def _node_value(self, name, cast=lambda x: x):
        match = self._comment.xpath(name)
        if not match and not len(match) > 0:
            return None

        return cast(match[0].text)

    @property
    def __name__(self):
        return self.cid

    @zeit.web.reify
    def uniqueId(self):  # NOQA
        return 'http://community.zeit.de/comment/{}'.format(self.cid)

    @zeit.web.reify
    def cid(self):
        return self._node_value('cid', int)

    @zeit.web.reify
    def uid(self):
        try:
            return self._node_value('uid', int)
        except TypeError:
            return

    @zeit.web.reify
    def title(self):
        return self._node_value('title')

    @zeit.web.reify
    def description(self):
        return self._node_value('description')

    @zeit.web.reify
    def publication_date(self):
        return zeit.web.core.date.parse_date(
            self._node_value('pubDate'),
            date_format='iso-8601')

    @zeit.web.reify
    def referenced_content(self):
        unique_id = self._node_value('cms_uniqueId')
        try:
            return zeit.cms.interfaces.ICMSContent(unique_id)
        except TypeError:
            return
