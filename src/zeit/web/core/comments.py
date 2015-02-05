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
                return _place_answers_under_parent(
                    lxml.etree.fromstring(response.content))
            except(IOError, lxml.etree.XMLSyntaxError):
                return
        else:
            return


def _place_answers_under_parent(xml):
    filter_xslt = lxml.etree.XML("""
        <xsl:stylesheet version="1.0"
            xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
            <xsl:output method="xml"
                        omit-xml-declaration="yes" />
          <xsl:template match="comments">
            <comments>
              <xsl:apply-templates select="comment_count" />
              <xsl:apply-templates select="last_comment_timestamp" />
              <xsl:apply-templates select="last_comment_name" />
              <xsl:apply-templates select="last_comment_uid" />
              <xsl:apply-templates select="nid" />
              <xsl:apply-templates select="path" />
              <xsl:apply-templates select="source" />
              <xsl:apply-templates select="comment">
                <xsl:sort select="./@id" order="descending" data-type="text" />
              </xsl:apply-templates>
            </comments>
          </xsl:template>
          <xsl:template match="comments/last_comment_timestamp">
            <xsl:copy-of select="." />
          </xsl:template>
          <xsl:template match="comments/last_comment_name">
            <xsl:copy-of select="." />
          </xsl:template>
          <xsl:template match="comments/last_comment_uid">
            <xsl:copy-of select="." />
          </xsl:template>
          <xsl:template match="comments/comment_count">
            <xsl:copy-of select="." />
          </xsl:template>
          <xsl:template match="nid">
            <xsl:copy-of select="." />
          </xsl:template>
          <xsl:template match="comments/comment">
          <xsl:variable name="cid"><xsl:value-of select="@id" /></xsl:variable>
            <xsl:if test="not(inreply)">
              <xsl:copy-of select="." />
            </xsl:if>
            <xsl:apply-templates select="//comment/inreply[@to=$cid]">
              <xsl:sort select="./@cid" order="ascending" data-type="text" />
            </xsl:apply-templates>
          </xsl:template>
          <xsl:template match="comments/path">
            <xsl:copy-of select="." />
          </xsl:template>
          <xsl:template match="comments/source">
            <xsl:copy-of select="." />
          </xsl:template>

          <xsl:template match="//comment/inreply">
            <xsl:copy-of select=".." />
          </xsl:template>

        </xsl:stylesheet>
    """)
    transform = lxml.etree.XSLT(filter_xslt)
    return transform(xml)


def comment_as_dict(comment, request):
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
        picture_url = (request.registry.settings.community_host + '/' +
                       comment.xpath('author/@picture')[0])
    else:
        picture_url = None

    if comment.xpath('author/@url'):
        profile_url = (request.registry.settings.community_host +
                       comment.xpath('author/@url')[0])

    if comment.xpath('content/text()'):
        content = comment.xpath('content/text()')[0]
    else:
        content = '[fehler]'

    dts = ('date/year/text()', 'date/month/text()', 'date/day/text()',
           'date/hour/text()', 'date/minute/text()')

    return dict(
        indented=bool(len(comment.xpath('inreply'))),
        recommended=bool(
            len(comment.xpath('flagged[@type="kommentar_empfohlen"]'))),
        img_url=picture_url,
        userprofile_url=profile_url,
        name=comment.xpath('author/name/text()')[0],
        timestamp=datetime.datetime(*(int(comment.xpath(d)[0]) for d in dts)),
        text=content,
        role=', '.join(roles),
        cid=comment.xpath('./@id')[0]
    )


def get_thread(unique_id, request):
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
    try:
        return dict(
            comments=[
                comment_as_dict(comment, request)
                for comment in thread.xpath('//comment')],
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
    except AssertionError:
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
