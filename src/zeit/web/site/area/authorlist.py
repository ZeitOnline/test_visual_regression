import grokcore.component

import zeit.web
import zeit.web.core.area.ranking


@zeit.web.register_area('author-list')
class AuthorList(zeit.web.core.area.ranking.Ranking):
    pass


class SolrContentQuery(zeit.web.core.area.ranking.SolrContentQuery):

    grokcore.component.context(AuthorList)

    FIELD_MAP = zeit.web.core.area.ranking.SolrContentQuery.FIELD_MAP.copy()
    FIELD_MAP.update({
        'author_summary_t': 'summary',
        'display_name_s': 'display_name',
    })

    def _convert(self, doc):
        doc = super(SolrContentQuery, self)._convert(doc)
        # Prevent proxy exposure for missing fields (e.g. probably the majority
        # of author objects does not have an image).
        for key in ['image', 'summary']:
            doc.setdefault(key, None)
        return doc
