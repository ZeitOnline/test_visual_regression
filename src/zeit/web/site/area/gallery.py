import random

import zeit.web

import zeit.content.cp.automatic
import zeit.content.cp.interfaces


@zeit.web.register_area('gallery')
class Gallery(zeit.content.cp.automatic.AutomaticArea):

    def _query_centerpage(self):
        teasers = list(zeit.content.cp.interfaces.ITeaseredContent(
            self.referenced_cp, []))
        return random.sample(
            teasers, min(len(teasers), self.count_to_replace_duplicates))
