# -*- coding: utf-8 -*-
import datetime
import string
import urlparse

import lxml.etree
import requests
import zope.component

import zeit.cms.interfaces

import zeit.web.core.interfaces


def path_of_article(unique_id):
    return urlparse.urlparse(unique_id).path[1:]


class Agatho(object):

    def __init__(self, agatho_url, timeout=5.0):
        self.entry_point = agatho_url
        self.timeout = timeout

    def collection_get(self, unique_id):
        try:
            response = requests.get(
                '%s%s' % (self.entry_point, path_of_article(unique_id)),
                timeout=self.timeout)
        except:  # yes, we really do want to catch *all* exceptions here!
            return
        if response.ok:
            try:
                return lxml.etree.fromstring(response.content)
            except (IOError, lxml.etree.XMLSyntaxError):
                return
        else:
            return


def comment_as_dict(comment):
    """Expects an lxml element representing an agatho comment and returns a
    dict representation."""

    if comment.xpath('author/@roles'):
        roles = string.split(comment.xpath('author/@roles')[0], ',')
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
        picture_url = comment.xpath('author/@picture')[0]
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

    if comment.xpath('inreply/@to'):
        in_reply = int(comment.xpath('inreply/@to')[0].lstrip('cid-'))
    else:
        in_reply = None

    dts = ('date/year/text()', 'date/month/text()', 'date/day/text()',
           'date/hour/text()', 'date/minute/text()')

    return dict(
        in_reply=in_reply,
        indented=bool(in_reply),
        recommended=bool(
            len(comment.xpath('flagged[@type="kommentar_empfohlen"]'))),
        img_url=picture_url,
        userprofile_url=profile_url,
        name=comment.xpath('author/name/text()')[0],
        timestamp=datetime.datetime(*(int(comment.xpath(d)[0]) for d in dts)),
        text=content,
        role=', '.join(roles),
        cid=int(comment.xpath('./@id')[0].lstrip('cid-'))
    )


def get_thread(unique_id, request, reverse=True):
    """Return a dict representation of the comment thread of the given
    article."""

    if 'agatho_host' not in request.registry.settings:
        return
    api = Agatho(
        agatho_url='%s/agatho/thread/' % request.registry.settings.agatho_host,
        timeout=float(request.registry.settings.community_host_timeout_secs)
    )
    thread = api.collection_get(unique_id)
    if thread is None:
        return

    # Read more about sorting in multiple passes here:
    # https://docs.python.org/2/howto/sorting.html#sort-stability-and-complex-sorts
    comments = list(comment_as_dict(c) for c in thread.xpath('//comment'))

    comments = sorted(comments, key=lambda x: x['cid'])

    comments = sorted(comments, key=lambda x: (x['in_reply'] or x['cid']),
                      reverse=reverse)

    try:
        return dict(
            comments=comments,
            comment_count=int(
                thread.xpath('/comments/comment_count')[0].text),
            nid=thread.xpath('/comments/nid')[0].text,
            # TODO: these urls should point to ourselves,
            # not to the 'back-backend'
            comment_post_url='%s/agatho/thread/%s?destination=%s' % (
                request.registry.settings.agatho_host,
                '/'.join(request.traversed),
                request.url),
            comment_report_url='%s/services/json' % (
                request.registry.settings.community_host))
    except (IndexError, AttributeError):
        return


def comments_per_unique_id():
    # XXX This should be registered as a utility instead of being recalculated
    #     on every call.
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    uri = 'http://xml.zeit.de/' + conf.get('node_comment_statistics')

    try:
        raw = zeit.cms.interfaces.ICMSContent(uri)
        nodes = lxml.etree.fromstring(raw.data.encode()).xpath('/nodes/node')
    except (lxml.etree.LxmlError, TypeError):
        return {}

    return {node.values()[1]: node.values()[0] for node in nodes}
