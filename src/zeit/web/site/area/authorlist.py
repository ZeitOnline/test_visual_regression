import zeit.web
import zeit.web.core.area.ranking


@zeit.web.register_area('author-list')
class AuthorList(zeit.web.core.area.ranking.Ranking):

    FIELDS = zeit.web.core.area.ranking.Ranking.FIELDS + ' ' + ' '.join([
        'author_summary_t',
        'display_name_s',
    ])

    FIELD_MAP = zeit.web.core.area.ranking.Ranking.FIELD_MAP + [
        (u'author_summary_t', 'summary'),
        (u'display_name_s', 'display_name'),
    ]

    def document_hook(self, doc):
        doc = super(AuthorList, self).document_hook(doc)
        # Prevent proxy exposure for missing fields (e.g. probably the majority
        # of author objects does not have an image).
        for key in ['image', 'summary']:
            if key not in doc:
                doc[key] = None
        return doc
