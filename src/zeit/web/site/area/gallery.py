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
    def total_pages(self):
        try:
            if self.hits + self.count > 0:
                return int(math.ceil(float(self.hits) / float(self.count)))
            else:
                return 0
        except TypeError:
            return 0

    @zeit.web.reify
    def next_page(self):
        if self.page < self.total_pages:
            return self.page + 1
        else:
            # Rewind to page 1
            return 1

    def _extract_newest(self, content):
        if not self.page_called.get(self.page, False):
            for i in range(0, (self.page * len(self.context.values())) - 1):
                teaser = super(Gallery, self)._extract_newest(content)
            self.page_called[self.page] = True
            return teaser

        return super(Gallery, self)._extract_newest(content)
