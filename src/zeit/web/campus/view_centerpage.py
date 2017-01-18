import zeit.content.cp.interfaces

import zeit.web
import zeit.web.campus.view
import zeit.web.core.view
import zeit.web.core.view_centerpage


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICP2015,
    custom_predicates=(zeit.web.campus.view.is_zco_content,
                       zeit.web.core.view.is_advertorial),
    renderer='templates/centerpage_advertorial.html')
@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICP2015,
    custom_predicates=(zeit.web.campus.view.is_zco_content,),
    renderer='templates/centerpage.html')
class Centerpage(
        zeit.web.core.view_centerpage.Centerpage,
        zeit.web.campus.view.Content):
    pass


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICP2015,
    custom_predicates=(zeit.web.campus.view.is_zco_content,
                       zeit.web.core.view.is_paginated),
    renderer='templates/centerpage.html')
class CenterpagePage(zeit.web.core.view_centerpage.CenterpagePage, Centerpage):
    pass
