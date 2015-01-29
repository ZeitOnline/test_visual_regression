# -*- coding: utf-8 -*-
import pyramid.view
import zeit.web.core.view
import zeit.web.magazin.view


def is_zon_content(context, request):
    """Custom predicate to verify, if this can be rendered via zeit.web
    :rtype: bool
    """

    # We might need to evaluate, if we have a rebrush_website_content again at
    # some point. So this is, how it would be done. (ron)
    #  return bool(getattr(context, 'rebrush_website_content', False)) and (
    #    not zeit.web.magazin.view.is_zmo_content(context, request))

    return bool(not zeit.web.magazin.view.is_zmo_content(context, request))


class Base(zeit.web.core.view.Base):

    def banner_toggles(self, name):
        try:
            return bool(zeit.web.core.banner.banner_toggles[name])
        except (IndexError, TypeError):
            return False


@pyramid.view.view_config(
    route_name='spektrum-kooperation',
    renderer='templates/inc/parquet/parquet-spektrum.html')
def spektrum_hp_feed(request):
    return {'row': {'id': 'my id'}}
