import grokcore.component
import pyramid.httpexceptions
import pyramid.threadlocal

import zeit.content.cp.automatic


@zeit.web.register_area('gallery')
class Gallery(zeit.content.cp.automatic.AutomaticArea):
    """An automatic area that offers pagination via a single "more" button
    that cycles through all available teasers (and starts from the beginning
    after reaching the end).
    """


class CyclicalContentQuery(zeit.content.cp.automatic.CenterpageContentQuery):

    grokcore.component.context(Gallery)

    def __call__(self):
        # Since we don't know which teasers on previous pages may have been
        # duplicates, we need to burn through all previous pages and consume
        # enough valid teasers of the content slice.
        request = pyramid.threadlocal.get_current_request()
        skip_until = request.GET.get('p', False)
        if skip_until and not skip_until.startswith(
                zeit.cms.interfaces.ID_NAMESPACE):
            raise pyramid.httpexceptions.HTTPNotFound()

        result = []
        teasered = iter([])
        while len(result) <= self.rows:
            try:
                content = next(teasered)
            except StopIteration:
                teasered = zeit.content.cp.interfaces.ITeaseredContent(
                    self.context.referenced_cp, None)
                if teasered is None:
                    break
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
