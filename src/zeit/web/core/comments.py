# -*- coding: utf-8 -*-

import pyramid.view
import zope.component
import pyramid.httpexceptions
import lxml.etree
import urlparse
import datetime
import requests
import requests.exceptions
from BeautifulSoup import BeautifulSoup
import repoze.lru

import zeit.cms.interfaces
import zeit.web.core.comments

from zeit.web.core.utils import to_int
import zeit.web.core.interfaces
import zeit.web.core.view

cache_maker= repoze.lru.CacheMaker()


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
        roles = comment.xpath('author/@roles')[0].split(',')
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
        recommendations=len(
            comment.xpath('flagged[@type="kommentar_empfohlen"]')),
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
    return get_cacheable_thread(unique_id, destination, reverse)

@cache_maker.expiring_lrucache(maxsize=1000, timeout=60, name='comment_thread')
def get_cacheable_thread(unique_id, destination, reverse):
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

def _is_admin(context, request):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    if conf.get('is_admin'):
        return True
    return request.client_addr == '127.0.0.1'


class PostComment(zeit.web.core.view.Base):
    """POST comments via http to configured community. Expects a
    request with at least a path to the resource or the nid in drupal and
    a comment.

    :param context, request: via pyramid view_callable
    """

    def __init__(self, context, request, path=None):
        if not request.authenticated_userid:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='No User',
                explanation='Please log in in order to comment')
        self.path = request.params.get('path') or path
        self.context = context
        self.request = request
        zwcs = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        self.community_host = zwcs.get('community_host')
        self.status = []

    def __call__(self):
        self.request.response.cache_expires(0)
        return {}

    def post_comment(self):
        request = self.request
        user = request.session['user']
        uid = user['uid']

        if request.method == "POST":

            if (not (self.path or request.params.get('nid'))
                and not request.params.get('comment')):
                    raise pyramid.httpexceptions.HTTPInternalServerError(
                        title='No comment could be posted',
                        explanation=('Path and comment are required'))

            unique_id = 'http://xml.zeit.de/[community_nid]'

            nid = request.params.get('nid')
            if not nid:
                unique_id = 'http://xml.zeit.de/{}'.format(self.path)
                nid = self._nid_by_comment_thread(unique_id)

            action_url = '{}/agatho/thread/{}'.format(
                self.community_host, request.params.get('path'))

            data = {'nid': nid,
                    'uid': uid,
                    'subject': '[empty]',
                    'comment': request.params.get('comment'),
                    'pid': request.params.get('pid')}
            response = requests.post(action_url, data=data,
                                     cookies=dict(request.cookies))

            if response.status_code >= 200 and response.status_code < 300:
                self.status.append('A comment for {} was posted'.format(
                    unique_id))
                # XXX: invalidate object from cache here!
                # use something like
                # cache_maker.__dict__['_cache']['comment_thread'].invalidate
            else:
                raise pyramid.httpexceptions.HTTPInternalServerError(
                    title='No comment could be posted',
                    explanation='No comment  for {} could be '
                                'posted.'.format(unique_id))

    def _nid_by_comment_thread(self, unique_id):
        request = self.request
        comment_thread = zeit.web.core.comments.get_thread(
            unique_id, destination=request.url)

        if comment_thread:
            return comment_thread['nid']

        nid = self._create_and_load_comment_thread(unique_id)['nid']
        if not nid:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='No comment thread',
                explanation='No comment thread for {} could be '
                    'created.'.format(unique_id))
        else:
            return nid

    def _create_and_load_comment_thread(self, unique_id):
        content = None
        try:
            content = zeit.cms.interfaces.ICMSContent(unique_id)
        except TypeError:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='Resource does not exist',
                explanation='The resource {} does not exist and there is'
                            'no comment_thread for it.'.format(unique_id))

        xml_str = lxml.etree.tostring(content.xml)
        headers = {
            'X-uniqueId': 'http://{}{}'.format(
                self.request.host, urlparse.urlparse(unique_id)[2]),
            'Content-Type': 'text/xml'}
        response = requests.post(
            '{}/agatho/commentsection'.format(self.community_host),
            headers=headers,
            data=xml_str)

        if not response.status_code >= 200 and not response.status_code < 300:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='Comment Section could not be created',
                explanation='The comment section for the resource {} '
                            'could not be created'.format(unique_id))

        self.status.append('A comment section for {} was created'.format(
            unique_id))

        return zeit.web.core.comments.get_thread(
            unique_id, destination=self.request.url)


@pyramid.view.view_config(route_name='post_test_comments',
                          renderer='templates/post_test_comments.html',
                          custom_predicates=(_is_admin,))
class PostCommentAdmin(PostComment):
    def __init__(self, context, request):
        super(PostCommentAdmin, self).__init__(context, request)
        self.context = zeit.content.article.article.Article()
        self.post_comment()
