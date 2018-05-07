import zeit.content.cp.interfaces

import zeit.web
import zeit.web.arbeit.view
import zeit.web.core.view
import zeit.web.core.view_centerpage


@zeit.web.view_defaults(
    context=zeit.content.cp.interfaces.ICP2015,
    vertical='zar')
@zeit.web.view_config(
    custom_predicates=(zeit.web.core.view.is_advertorial,),
    renderer='templates/centerpage_advertorial.html')
@zeit.web.view_config(
    renderer='templates/centerpage.html')
class Centerpage(
        zeit.web.core.view_centerpage.Centerpage,
        zeit.web.arbeit.view.Base):
    pass


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICP2015,
    vertical='zar',
    custom_predicates=(zeit.web.core.view.is_paginated,),
    renderer='templates/centerpage.html')
class CenterpagePage(zeit.web.core.view_centerpage.CenterpagePage, Centerpage):
    pass
