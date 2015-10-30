import pyramid.threadlocal

import zope.schema

import zeit.cms.content.property
import zeit.content.cp.automatic


@zeit.web.register_area('gallery')
class Gallery(zeit.content.cp.automatic.AutomaticArea):

    # XXX: this is all very boilerplate-y, but it's get sh*t done
    #      nevertheless: refactoring would be great (aps)

    _hits = zeit.cms.content.property.ObjectPathProperty(
        '.hits', zope.schema.Int(required=False))
    _page = zeit.cms.content.property.ObjectPathProperty(
        '.page', zope.schema.Int(required=False))

    def __init__(self, context):
        super(Gallery, self).__init__(context)
        self.page_called = {}

    @property
    def count_to_replace_duplicates(self):
        return self.MINIMUM_COUNT_TO_REPLACE_DUPLICATES + (
            (self.page - 1) * self.count)

    @property
    def hits(self):
        if self._hits is None:
            self.values()
        return self._hits or 0

    @hits.setter
    def hits(self, value):
        if self._hits is None:
            self._hits = value

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
        # Deduplicate automatic gallery areas for pagination.
        #
        # Since we don't know which areas on previous pages may have been
        # duplicates, we cannot paginate properly after slicing the already
        # tidied up resultset.
        # Therefore we need to memorize all previous pages and reiterate
        # through all areas on each request, regardless of the current page, to
        # be able to paginate the whole, deduplicated resultset.
        #
        # Please wear your neo glasses.

        if not self.page_called.get(self.page, False):
            for i in range(0, (self.page * len(self.context.values())) - 1):
                teaser = super(Gallery, self)._extract_newest(
                    content, predicate)
                if teaser is None:
                    # Last page processing
                    #
                    # When our area list is exhausted, we have to start over
                    # again. Unfortunately this implies that the last page may
                    # contain all items from the first one, since we get to
                    # know whether there are no areas left, when we actually
                    # have reached the end of the list.
                    # => duplicated content?
                    self._rewind_page_processing()
                    teaser = super(Gallery, self)._extract_newest(
                        content, predicate)
            self.page_called[self.page] = True
            return teaser

        return super(Gallery, self)._extract_newest(content, predicate)

    def _rewind_page_processing(self):
        self.page = 1
        self._v_retrieved_content = 0
        self._v_try_to_retrieve_content = True
        self.page_called = {}
