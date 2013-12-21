# -*- coding: utf-8 -*-
import urlparse
from lxml import etree

def path_of_article(unique_id):
    return urlparse.urlparse(unique_id).path[1:]

class Agatho(object):

    def __init__(self, agatho_url):
        self.entry_point = agatho_url

    def collection_get(self, unique_id):
        try:
            return etree.parse('%s%s' % (self.entry_point, path_of_article(unique_id)))
        except IOError: # lxml reports a 404 as IOError, 404 code signals that no thread exists for that article
            return None


def comment_as_json(comment):
    """ expects an lxml element representing an agatho comment and returns a
    dict representation """
    return dict(indented=bool(len(comment.xpath('inreply'))),
        img_url=u'',
        name=comment.xpath('author/name/text()')[0],
        timestamp=None, # todo: parse date element
        role=False,
        text=comment.xpath('content/text()')[0])

def get_thread(unique_id, request):
    """ return a dict representation of the comment thread of the given article"""
    api = Agatho(request.registry.settings.agatho_url)
    thread = api.collection_get(unique_id)
    if thread is not None:
        return dict(
            comments=[comment_as_json(comment) for comment in thread.xpath('//comment')],
            comment_count=int(thread.xpath('/comments/comment_count')[0].text))
    else:
        return None
