import copy
import itertools
import uuid
import logging

import zeit.web
import zeit.web.site.area.ranking


log = logging.getLogger(__name__)


SANITY_BOUND = 1024


@zeit.web.register_area('overview')
class Overview(zeit.web.site.area.ranking.Ranking):

    count = SANITY_BOUND

    @property
    def placeholder(self):
        values = self.context.values()
        length = len(values)
        if not length or self.hits <= length:
            return iter(values)
        clones = self.clone_factory(values[-1], self.hits - length)
        return itertools.chain(values, clones)

    @staticmethod
    def clone_factory(jango, count):
        for _ in range(count):
            clone = copy.deepcopy(jango)
            clone.__name__ = str(uuid.uuid4())
            yield clone
