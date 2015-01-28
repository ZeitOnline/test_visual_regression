# -*- coding: utf-8 -*-
import mock

import zeit.cms.interfaces

import zeit.web.core.banner
import zeit.web.site


def test_banner_toggles_should_return_value(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/zeitonline')
    view = zeit.web.site.view_centerpage.Centerpage(context, mock.Mock())
    assert view.banner_toggles('testing_me') is False
