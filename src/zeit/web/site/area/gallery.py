import grokcore.component
import pyramid.threadlocal

import zeit.content.cp.automatic


@zeit.web.register_area('gallery')
class Gallery(zeit.content.cp.automatic.AutomaticArea):
    pass


class CyclicalContentQuery(zeit.content.cp.automatic.CenterpageContentQuery):

    grokcore.component.context(Gallery)

    def __call__(self):
        # Since we don't know which teasers on previous pages may have been
        # duplicates, we need to burn through all previous pages and consume
        # enough valid teasers of the content slice.
        request = pyramid.threadlocal.get_current_request()
        skip_until = request.GET.get('p', None)

        result = []
        teasered = iter([])
        while len(result) <= self.rows:
            try:
                content = next(teasered)
            except StopIteration:
                teasered = zeit.content.cp.interfaces.ITeaseredContent(
                    self.context.referenced_cp, iter([]))
                continue

            if self.context.hide_dupes and content in self.existing_teasers:
                continue
            if content.uniqueId == skip_until:
                skip_until = False
                continue  # Skip until and including
            if skip_until:
                continue
            result.append(content)
        return result
