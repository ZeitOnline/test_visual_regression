# -*- coding: utf-8 -*-
import collections
import datetime
import logging
import math

from BeautifulSoup import BeautifulSoup
import babel.dates
import beaker.cache
import lxml.etree
import requests
import requests.exceptions
import zope.component

import zeit.cms.interfaces

import zeit.web.core.interfaces
import zeit.web.core.template


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
    if comment.xpath('author/@roles'):
        roles = comment.xpath('author/@roles')[0]
        is_author = 'author' in roles
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
                       u'freelancer_weiblich': 'Freie Autorin',
                       u'freelancer_männlich': 'Freier Autor'}

        roles = [roles_words['%s_%s' % (role, gender)] for role in roles
                 if '%s_%s' % (role, gender) in roles_words]
    else:
        is_author = False
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
        in_reply=in_reply,
        img_url=picture_url,
        userprofile_url=profile_url,
        name=comment.xpath('author/name/text()')[0],
        created=created,
        text=content,
        role=', '.join(roles),
        fans=','.join(fans),
        cid=int(comment.xpath('./@id')[0].lstrip('cid-')),
        recommendations=len(
            comment.xpath('flagged[@type="leser_empfehlung"]')),
        is_author=is_author,
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
    timeout = float(conf.get('community_host_timeout_secs', 5))
    uri = '{}/agatho/thread{}'.format(
        conf.get('agatho_host', ''), path.encode('utf-8'))
    try:
        response = requests.get(uri, timeout=timeout)
        return response.ok and response.content or None
    except (AttributeError, requests.exceptions.RequestException):
        return


def get_thread(unique_id, sort='asc', page=None, cid=None):
    """Return a dict representation of the comment thread of the given
    article.

    :param sort: Sort order of comments, desc or asc
    :param page: Pagination value
    :param cid: Comment ID to calculate appropriate pagination
    :rtype: dict or None
    """
    thread = get_cacheable_thread(unique_id)
    if thread is None or thread['comment_count'] == 0:
        return

    # We do not want to touch the references of the cached thread
    thread = thread.copy()
    sorted_tree = thread['sorted_tree'].values()
    del thread['sorted_tree']

    thread['sort'] = sort
    if (sort == 'desc'):
        sorted_tree = reversed(sorted_tree)
    elif (sort == 'promoted'):
        sorted_tree = []
        for comment in thread['flattened_comments']:
            if comment['is_promoted'] is True:
                comment['is_reply'] = False
                sorted_tree.append([comment, []])
    elif (sort == 'recommended'):
        def comment_helper(comment):
            comment[0]['is_reply'] = False
            return comment[0]['recommendations']

        # Sort comment thread by recommendations
        # for comments with at least one recommendation
        sorted_tree = sorted(
            ([comment, []] for comment in thread['flattened_comments'] if (
                comment['recommendations'] > 0)),
            key=comment_helper,
            reverse=True)

    comments = []
    positional_index = {}
    for main_comment in sorted_tree:
        positional_index[main_comment[0]['cid']] = len(comments)
        comments.append(main_comment[0])
        for sub_comment in main_comment[1]:
            positional_index[sub_comment['cid']] = len(comments)
            comments.append(sub_comment)

    thread['comments'] = comments

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    page_size = int(conf.get('comment_page_size', '10'))

    comment_count = len(thread['comments'])
    pages = int(math.ceil(float(comment_count) / float(page_size)))

    # sanitize page value
    if page:
        try:
            page = int(page)
        except ValueError:
            page = 1

        if page < 1 or page > pages:
            page = 1

    # find page by cid
    if cid:
        try:
            pos = positional_index[int(cid)] + 1
            page = int(math.ceil(float(pos) / float(page_size)))
        except (KeyError, ValueError):
            pass

    thread['headline'] = '{} {}'.format(
        comment_count, 'Kommentar' if comment_count == 1 else 'Kommentare')
    thread['pages'] = {
        'current': page,
        'total': pages,
        'pager': zeit.web.core.template.calculate_pagination(page, pages)
    }

    if page:
        thread['comments'] = (
            thread['comments'][(page - 1) * page_size: page * page_size])

        if thread['pages']['pager']:
            first = ((page - 1) * page_size) + 1
            last = min(comment_count, ((page - 1) * page_size) + page_size)

            if first == last:
                thread['pages']['title'] = u'Kommentar {} von {}'.format(
                    first, comment_count)
            else:
                thread['pages']['title'] = u'Kommentar {} – {} von {}'.format(
                    first, last, comment_count)

    return thread


@beaker.cache.cache_region('long_term', 'comment_thread')
def get_cacheable_thread(unique_id):

    path = unique_id.replace(zeit.cms.interfaces.ID_NAMESPACE, '/', 1)
    thread = request_thread(path)

    if thread is None:
        return

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
    sorted_tree, index = _sort_comments(comment_list)

    try:
        return dict(
            sorted_tree=sorted_tree,
            flattened_comments=flattened_comments,
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
            comment['shown_num'] = str(
                comments_sorted.keys().index(comment['cid']) + 1)
        else:
            try:
                ancestor = root_ancestors[comment['in_reply']]
                root_ancestors[comment['cid']] = ancestor
                comments_sorted[ancestor][1].append(comment)
                p_index = comments_sorted[ancestor][0]['shown_num']
                comment['shown_num'] = "{}.{}".format(p_index, len(
                    comments_sorted[ancestor][1]))
            except KeyError:
                log.error("The comment with the cid {} is a reply, but"
                          "no ancestor could be found".format(comment['cid']))
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
        response = requests.post(uri, data=[('unique_ids[]', uid) for uid in
                                            unique_ids], timeout=timeout)
        return response.ok and response.content or None
    except (AttributeError, requests.exceptions.RequestException):
        return


def get_counts(*unique_ids):
    """Return a dictionary containing comment counts for a select set of
    content resources. If no resources are specified, the most commented
    resources will be used.

    :param unique_ids: Optional list of uniqueIds
    :rtype: dict
    """

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)

    if len(unique_ids):
        raw = request_counts(*unique_ids)
        if not raw:
            return {}
    else:
        uri = zeit.cms.interfaces.ID_NAMESPACE + conf.get(
            'node_comment_statistics', '')
        try:
            raw = zeit.cms.interfaces.ICMSContent(uri).data.encode()
        except (AttributeError, TypeError):
            return {}
    try:
        ascii = raw.encode('ascii', 'xmlcharrefreplace').strip()
        nodes = lxml.etree.fromstring(ascii).xpath('/nodes/node')
        return {zeit.cms.interfaces.ID_NAMESPACE.rstrip('/') + n.attrib['url']:
                n.attrib['comment_count'] for n in nodes}
    except (AttributeError, IndexError, KeyError, lxml.etree.LxmlError):
        return {}
