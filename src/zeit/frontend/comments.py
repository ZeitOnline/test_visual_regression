# -*- coding: utf-8 -*-
import urlparse
from datetime import datetime
from lxml import etree
from random import randint

from pyramid.view import view_config
import zeit.content.article.interfaces

def path_of_article(unique_id):
    return urlparse.urlparse(unique_id).path[1:]

class Agatho(object):

    def __init__(self, agatho_url):
        self.entry_point = agatho_url

    def collection_get(self, unique_id):
        try:
            return _place_answers_under_parent(etree.parse('%s%s' % (self.entry_point, path_of_article(unique_id))))
        except IOError: # lxml reports a 404 as IOError, 404 code signals that no thread exists for that article
            return None

def _place_answers_under_parent(xml):
    filter_xslt = etree.XML('''
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
    ''')
    transform = etree.XSLT(filter_xslt)
    #import pdb; pdb.set_trace();
    return transform(xml)

def comment_as_json(comment):
    """ expects an lxml element representing an agatho comment and returns a
    dict representation """
    if comment.xpath('author/@roles'):
      roles = comment.xpath('author/@roles')[0]
    else:
      roles = ''

    if comment.xpath('content/text()'):
      content=comment.xpath('content/text()')[0]
    else:
      content = '[fehler]'
    return dict(indented=bool(len(comment.xpath('inreply'))),
        img_url=u'',
        name=comment.xpath('author/name/text()')[0],
        timestamp=datetime(int(comment.xpath('date/year/text()')[0]),
                           int(comment.xpath('date/month/text()')[0]),
                           int(comment.xpath('date/day/text()')[0]),
                           int(comment.xpath('date/hour/text()')[0]),
                           int(comment.xpath('date/minute/text()')[0])),
        role=roles,
        text=content)

def get_thread(unique_id, request):
    """ return a dict representation of the comment thread of the given article"""
    api = Agatho(request.registry.settings.agatho_url)
    thread = api.collection_get(unique_id)
    if thread is not None:
        return dict(
            comments=[comment_as_json(comment) for comment in thread.xpath('//comment')],
            comment_count=int(thread.xpath('/comments/comment_count')[0].text),
            nid=thread.xpath('/comments/nid')[0].text,
            my_uid=request.cookies.get('drupal-userid', 0))
    else:
        return dict(comments=[], comment_count=0)


from cornice.resource import resource, view
from zeit.frontend import COMMENT_COLLECTION_PATH, COMMENT_PATH

def unique_id_factory(request):
    return '/'.join([u'http://xml.zeit.de'] + list(request.matchdict['subpath']))


@resource(collection_path=COMMENT_COLLECTION_PATH, path=COMMENT_PATH, factory=unique_id_factory)
class Comment(object):

    def __init__(self, context, request):
        self.unique_id = context
        self.request = request

    @view(renderer='json')
    def collection_get(self):
        return get_thread(self.unique_id, self.request)
