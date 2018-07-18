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

    TEASER_FIELDS = {
        'teaserSupertitle': 'supertitle',
        'teaserTitle': 'title',
        'teaserText': 'subtitle',
    }

    @classmethod
    def _set_defaults(cls, doc):
        # XXX These asset badges and classification flags are not indexed
        #     in Solr, so we lie about them.
        for name in ['gallery', 'genre', 'template', 'video', 'video_2']:
            doc.setdefault(name, None)
        doc.setdefault('access', 'free')
        doc.setdefault('commentsAllowed', True)
        doc.setdefault('commentSectionEnable', True)
        doc.setdefault('date_last_published_semantic', None)
        doc.setdefault('lead_candidate', False)
        doc.setdefault('ressort', None)
        doc.setdefault('sub_ressort', None)
        doc.setdefault('supertitle', None)
        doc.setdefault('title', None)
        doc.setdefault('tldr_title', None)
        doc.setdefault('tldr_text', None)
        doc.setdefault('tldr_date', None)
        doc.setdefault('tldr_milestone', None)
        # Imported news articles don't have a teaser section
        for teaser, fallback in cls.TEASER_FIELDS.items():
            if not doc.get(teaser):
                doc[teaser] = doc.get(fallback)
        return doc


class FakeReference(object):

    def __init__(self, content):
        self.target = content


class SolrContentQuery(zeit.content.cp.automatic.SolrContentQuery,
                       Converter):

    FIELD_MAP = {
        'access': '',
        'authors': '',
        'comments': 'commentsAllowed',
        'date-last-modified': 'date_last_modified',
        'date-first-released': 'date_first_released',
        'date_last_published': '',
        'date_last_published_semantic': 'date_last_published_semantic',
        'id': '',
        'image-base-id': 'teaser_image',
        'image-fill-color': 'teaser_image_fill_color',
        'keyword': '',
        'keyword_id': '',
        'last-semantic-change': 'last_semantic_change',
        'lead_candidate': '',
        'product_id': '',
        'ressort': '',
        'serie': '',
        'show_commentthread': 'commentSectionEnable',
        'supertitle': '',
        'teaser_supertitle': 'teaserSupertitle',
        'teaser_text': 'teaserText',
        'teaser_title': 'teaserTitle',
        'title': '',
        'type': 'doc_type',
        'uniqueId': '',
    }

    @zeit.web.reify
    def FIELDS(self):  # NOQA
        return ' '.join(self.FIELD_MAP.keys())

    def _convert(self, doc):
        doc = super(SolrContentQuery, self)._convert(doc)
        for key in ['teaser_image', 'teaser_image_fill_color']:
            if doc.get(key):
                doc[key] = doc[key][0]
        return doc

    def _resolve(self, doc):
        return zeit.cms.interfaces.ICMSContent(self._convert(doc), None)


class TMSContentQuery(zeit.content.cp.automatic.TMSContentQuery):

    def _resolve(self, doc):
        content = zeit.retresco.interfaces.ITMSContent(doc)
        zeit.web.core.repository.add_marker_interfaces(
            content, in_repository=False)
        return content


class ElasticsearchContentQuery(
        zeit.content.cp.automatic.ElasticsearchContentQuery):

    include_payload = True

    def _resolve(self, doc):
        content = zeit.retresco.interfaces.ITMSContent(doc)
        zeit.web.core.repository.add_marker_interfaces(
            content, in_repository=False)
        return content


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
        except Exception:
            log.warning(
                'Error retrieving topic pages for %s',
                self.context.uniqueId, exc_info=True)
        return result
