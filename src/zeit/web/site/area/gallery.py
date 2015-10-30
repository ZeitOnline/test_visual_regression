import math

import pyramid.threadlocal

import zope.schema

import zeit.cms.content.property
import zeit.content.cp.automatic
import zeit.content.cp.interfaces


@zeit.web.register_area('gallery')
class Gallery(zeit.content.cp.automatic.AutomaticArea):

    # XXX: this is all very boilerplate-y, but it's get sh*t done
    #      nevertheless: refactoring would be great (aps)

    _hits = zeit.cms.content.property.ObjectPathProperty(
        '.hits', zope.schema.Int(required=False))

    def __init__(self, context):
        super(Gallery, self).__init__(context)
        self.page_called = {}
        # Will have to mess with the page number for last page processing,
        # which we cannot do with self.page directly.
        self._page = self.page

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
        try:
            return int(pyramid.threadlocal.get_current_request().GET['p'])
        except (KeyError, ValueError):
            return 1

    @zeit.web.reify
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
        if not self.page_called.get(self.page, False):
            for i in range(0, (self.page * len(self.context.values())) - 1):
                teaser = super(Gallery, self)._extract_newest(
                    content, predicate)
            self.page_called[self.page] = True
            self._hits = len(self.context.values()) + 2
            return teaser

        return super(Gallery, self)._extract_newest(content, predicate)
