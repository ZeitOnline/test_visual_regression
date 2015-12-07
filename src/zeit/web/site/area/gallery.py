import pyramid.threadlocal

import zeit.content.cp.automatic


@zeit.web.register_area('gallery')
class Gallery(zeit.content.cp.automatic.AutomaticArea):

    def __init__(self, context):
        super(Gallery, self).__init__(context)
        request = pyramid.threadlocal.get_current_request()
        self.skip_until = self.next_page = request.GET.get('p', None)

    def _extract_newest(self, content, predicate=None):
        # Deduplicate automatic gallery area for pagination.
        #
        # Since we don't know which teasers on previous pages may have been
        # duplicates, we need to burn through all previous pages and consume
        # enough valid teasers of the content slice.

        while self.skip_until:
            if len(content) == 0:
                more_content = self._retrieve_content()
                if more_content:
                    content[:] = more_content
            teaser = super(Gallery, self)._extract_newest(content, predicate)
            if teaser is None or teaser.uniqueId == self.skip_until:
                self.skip_until = None

        teaser = super(Gallery, self)._extract_newest(content, predicate)
        if teaser:
            self.next_page = teaser.uniqueId
            return teaser
        else:
            self._v_retrieved_content = 0
            self._v_try_to_retrieve_content = True
            return super(Gallery, self)._extract_newest(content, predicate)
