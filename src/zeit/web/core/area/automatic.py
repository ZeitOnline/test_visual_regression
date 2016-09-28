import collections
import logging

import grokcore.component
import zc.iso8601.parse
import zope.component

import zeit.cms.interfaces
import zeit.cms.tagging.interfaces
import zeit.content.cp.automatic


log = logging.getLogger(__name__)


class Converter(object):

    def _convert(self, doc):
        doc = self._convert_names(doc)
        doc = self._convert_dates(doc)
        doc = self._set_defaults(doc)
        return doc

    FIELD_MAP = NotImplemented

    def _convert_names(self, doc):
        for source, target in self.FIELD_MAP.items():
            try:
                doc[target] = doc[source]
            except KeyError:
                continue
        return doc

    DATE_FIELDS = [
        'date_last_modified',
        'date_first_released',
        'last_semantic_change',
        'date_last_published',
        'date_last_published_semantic',
    ]

    def _convert_dates(self, doc):
        for key in self.DATE_FIELDS:
            try:
                doc[key] = zc.iso8601.parse.datetimetz(str(doc[key]))
            except (KeyError, UnicodeEncodeError, ValueError):
                continue
        return doc

    def _convert_authorships(self, doc):
        # Not generally applicable, since solr does not index author uniqueIds.
        doc['authorships'] = [
            FakeReference(zeit.cms.interfaces.ICMSContent(x, None))
            for x in doc.get('authorships', ())]
        return doc

    def _set_defaults(self, doc):
        # XXX These asset badges and classification flags are not indexed
        #     in Solr, so we lie about them.
        for name in ['gallery', 'genre', 'template', 'video', 'video_2']:
            doc.setdefault(name, None)
        doc.setdefault('lead_candidate', False)
        doc.setdefault('commentSectionEnable', True)
        doc.setdefault('access', 'free')
        return doc


class FakeReference(object):

    def __init__(self, content):
        self.target = content


class SolrContentQuery(zeit.content.cp.automatic.SolrContentQuery,
                       Converter):

    FIELD_MAP = {
        'access': '',
        'authors': '',
        'date-last-modified': 'date_last_modified',
        'date_first_released': '',
        'date_last_published': '',
        'date_last_published_semantic': 'date_last_published_semantic',
        'image-base-id': 'teaser_image',
        'image-fill-color': 'teaser_image_fill_color',
        'last-semantic-change': 'last_semantic_change',
        'lead_candidate': '',
        'product_id': '',
        'serie': '',
        'show_commentthread': 'commentSectionEnable',
        'supertitle': 'teaserSupertitle',
        'teaser_text': 'teaserText',
        'title': 'teaserTitle',
        'type': 'doc_type',
        'uniqueId': '',
    }

    @zeit.web.reify
    def FIELDS(self):
        return ' '.join(self.FIELD_MAP.keys())

    def _convert(self, doc):
        doc = super(SolrContentQuery, self)._convert(doc)
        for key in ['teaser_image', 'teaser_image_fill_color']:
            if doc.get(key):
                doc[key] = doc[key][0]
        return doc

    def _resolve(self, doc):
        return zeit.cms.interfaces.ICMSContent(self._convert(doc), None)


class TMSContentQuery(zeit.content.cp.automatic.TMSContentQuery,
                      Converter):

    # XXX Can we generate this from zeit.retresco.convert somehow?
    FIELD_MAP = collections.OrderedDict((
        ('authors', 'authorships'),
        ('author_names', 'authors'),
        ('date_last_semantic_change', 'last_semantic_change'),
        ('allow_comments', 'commentsAllowed'),
        ('show_comments', 'commentSectionEnable'),
        ('print_ressort', 'printRessort'),
        ('teaser_text', 'teaserText'),
        ('teaser_title', 'teaserTitle'),
        ('teaser_supertitle', 'teaserSupertitle'),
        ('article_genre', 'genre'),
        ('article_template', 'template'),
    ))

    def _convert(self, doc):
        doc = super(TMSContentQuery, self)._convert(doc)
        doc = self._convert_authorships(doc)
        return doc

    def _resolve(self, doc):
        return zeit.cms.interfaces.ICMSContent(self._convert(doc), None)


class ElasticsearchContentQuery(
        zeit.content.cp.automatic.ElasticsearchContentQuery,
        Converter):

    include_payload = True
    FIELD_MAP = TMSContentQuery.FIELD_MAP

    def _convert(self, doc):
        doc = super(ElasticsearchContentQuery, self)._convert(doc)
        doc = self._convert_authorships(doc)
        return doc

    def _resolve(self, doc):
        return zeit.cms.interfaces.ICMSContent(self._convert(doc), None)


class TopicsitemapContentQuery(zeit.content.cp.automatic.ContentQuery):

    grokcore.component.name('topicsitemap')

    def __call__(self):
        self.total_hits = 0
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        result = []
        try:
            topics = zope.component.getUtility(
                zeit.cms.tagging.interfaces.ITopicpages)
            response = topics.get_topics(self.start, self.rows)
            self.total_hits = response.hits
            for item in response:
                content = zeit.cms.interfaces.ICMSContent({
                    'uniqueId': u'{}/{}'.format(
                        conf.get('topic_prefix', ''), item['id']),
                    'title': item['title'],
                }, None)
                if content is not None:
                    result.append(content)
        except:
            log.warning(
                'Error retrieving topic pages for %s',
                self.context.uniqueId, exc_info=True)
        return result
