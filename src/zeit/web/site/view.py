# -*- coding: utf-8 -*-
import zeit.web.core.view
import zeit.web.magazin.view


def is_zon_content(context, request):
    """Custom predicate to verify, if this can be rendered via zeit.frontend
    :rtype: str
    """

    # return bool(getattr(context, 'rebrush_website_content', False)) and (
    #     not zeit.web.magazin.view.is_zmo_content(context, request))

    return (not zeit.web.magazin.view.is_zmo_content(context, request))


class Base(zeit.web.core.view.Base):

    def banner_toggles(self, name):
        try:
            return bool(zeit.web.core.banner.banner_toggles[name])
        except IndexError:
            return False
