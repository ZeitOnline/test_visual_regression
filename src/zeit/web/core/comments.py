# -*- coding: utf-8 -*-
import datetime

import lxml.etree
import requests
import requests.exceptions
import zope.component
from BeautifulSoup import BeautifulSoup

import zeit.cms.interfaces

from zeit.web.core.utils import to_int
import zeit.web.core.interfaces


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

    # We have the drupal behaviour that the subject is partly coypied from the
    # comment itself, if a subject was not set. This leads to a slightly more
    # complex evaluation of the subject in our usecase
    subject = comment.xpath('subject/text()')
    content_stripped = ''.join(BeautifulSoup(content).findAll(text=True))
    if (subject and not subject[0] == '[empty]' and
            not subject[0] == content_stripped[0:len(subject[0])]):
        content = u'<p>{}</p>{}'.format(comment.xpath('subject/text()')[0],
                                        content)

    if comment.xpath('inreply/@to'):
        in_reply = int(comment.xpath('inreply/@to')[0].lstrip('cid-'))
    else:
        in_reply = None

    dts = ('date/year/text()', 'date/month/text()', 'date/day/text()',
           'date/hour/text()', 'date/minute/text()')

    # TODO: Catch name, timestamp and cid unavailabilty in element tree.
    return dict(
        in_reply=in_reply,
        indented=bool(in_reply),
        img_url=picture_url,
        userprofile_url=profile_url,
        name=comment.xpath('author/name/text()')[0],
        timestamp=datetime.datetime(*(int(comment.xpath(d)[0]) for d in dts)),
        text=content,
        role=', '.join(roles),
        cid=int(comment.xpath('./@id')[0].lstrip('cid-')),
        recommendations=len(
            comment.xpath('flagged[@type="kommentar_empfohlen"]')),
        is_recommended=bool(
            len(comment.xpath('flagged[@type="kommentar_empfohlen"]'))),
        is_author=is_author
    )


def request_thread(path):
    """Send a GET request to receive an agatho comment thread.

    :param path: Path section of a uniqueId
    :rtype: unicode or None
    """

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    timeout = float(conf.get('community_host_timeout_secs', 5))
    uri = '{}/agatho/thread{}'.format(conf.get('agatho_host', ''), path)
    try:
        response = requests.get(uri, timeout=timeout)
        return response.ok and response.content or None
    except (AttributeError, requests.exceptions.RequestException):
        return


def get_thread(unique_id, destination=None, reverse=False):
    """Return a dict representation of the comment thread of the given
    article.

    :param destination: URL of the redirect destination
    :param reverse: Reverse the chronological sort order of comments
    :rtype: dict or None
    """

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)

    path = unique_id.replace(zeit.cms.interfaces.ID_NAMESPACE, '/', 1)
    thread = request_thread(path)

    if thread is None:
        return

    try:
        document = lxml.etree.fromstring(thread)
    except (IOError, lxml.etree.XMLSyntaxError):
        return

    try:
        comment_count = document.xpath('/comments/comment_count/text()')[0]
        comment_nid = document.xpath('/comments/nid/text()')[0]
        comment_list = document.xpath('//comment')
    except (IndexError, lxml.etree.XMLSyntaxError):
        return

    # Read more about sorting in multiple passes here:
    # docs.python.org/2/howto/sorting.html#sort-stability-and-complex-sorts
    comments = list(comment_to_dict(c) for c in comment_list)
    comments = sorted(comments, key=lambda x: x['cid'])
    comments = sorted(comments, key=lambda x: (x['in_reply'] or x['cid']),
                      reverse=reverse)
    try:
        return dict(
            comments=comments,
            comment_count=to_int(comment_count),
            nid=comment_nid,
            comment_post_url='{}/agatho/thread{}?destination={}'.format(
                conf.get('agatho_host', ''), path, destination),
            comment_report_url='{}/services/json'.format(
                conf.get('community_host', '')))
    except (IndexError, AttributeError):
        return


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
