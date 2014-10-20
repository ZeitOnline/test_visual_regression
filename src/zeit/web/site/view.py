# -*- coding: utf-8 -*-
import zeit.web.magazin.view


def is_zon_content(context, request):
    """Custom predicate to verify, if this can be rendered via zeit.frontend
    :rtype: str
    """

    return bool(getattr(context, 'rebrush_website_content', False)) and (
        not zeit.web.magazin.view.is_zmo_content(context, request))
