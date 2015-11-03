import pyramid.threadlocal

import zeit.cms.content.property
import zeit.content.cp.automatic


@zeit.web.register_area('gallery')
class Gallery(zeit.content.cp.automatic.AutomaticArea):

    def __init__(self, context):
        super(Gallery, self).__init__(context)
        self.skip_previous_pages = True
        self._page = None

    @property
    def count_to_replace_duplicates(self):
        return self.MINIMUM_COUNT_TO_REPLACE_DUPLICATES + (
            (self.page - 1) * self.count)

    @property
    def page(self):
        if self._page is None:
            request = pyramid.threadlocal.get_current_request()
            try:
                self._page = int(request.GET['p'])
            except (KeyError, ValueError):
                self._page = 1
        return self._page

    @page.setter
    def page(self, value):
        self._page = value

    @property
    def next_page(self):
        return self.page + 1

    def _extract_newest(self, content, predicate=None):
        # Deduplicate automatic gallery area for pagination.
        #
        # Since we don't know which teasers on previous pages may have been
        # duplicates, we need to burn through all previous pages and consume
        # enough valid teasers of the content slice.

        if self.skip_previous_pages:
            for _ in range((self.page - 1) * self.context.count):
                super(Gallery, self)._extract_newest(content, predicate)
            else:
                self._v_retrieved_content = 0
                self._v_try_to_retrieve_content = True
                self.skip_previous_pages = False

        return super(Gallery, self)._extract_newest(content, predicate)
