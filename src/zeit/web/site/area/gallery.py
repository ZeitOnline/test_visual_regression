import math

import zope.schema

import zeit.cms.content.property
import zeit.content.cp.automatic
import zeit.content.cp.interfaces


@zeit.web.register_area('gallery')
class Gallery(zeit.content.cp.automatic.AutomaticArea):

    # XXX: this is all very boilerplate-y, but it's get sh*t done
    #      nevertheless: refactoring would be great (aps)

    _page = zeit.cms.content.property.ObjectPathProperty(
        '.page', zope.schema.Int(required=False))
    _hits = zeit.cms.content.property.ObjectPathProperty(
        '.hits', zope.schema.Int(required=False))

    def values(self):
        return self._values

    @zeit.web.reify
    def _values(self):
        return super(Gallery, self).values()

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
            return 1
        return self._page

    @page.setter
    def page(self, value):
        self._page = value

    @zeit.web.reify
    def total_pages(self):
        if self.hits + self.count > 0:
            return int(math.ceil(float(self.hits) / float(self.count)))
        else:
            return 0

    @zeit.web.reify
    def next_page(self):
        if self.page < self.total_pages:
            return self.page + 1

    def _query_centerpage(self):
        teasers = list(zeit.content.cp.interfaces.ITeaseredContent(
            self.referenced_cp, []))
        self._hits = len(teasers)
        return teasers[(self.page - 1) * self.count:self.page * self.count]
