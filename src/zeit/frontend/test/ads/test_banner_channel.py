# -*- coding: utf-8 -*-
import mock

import zeit.cms.interfaces
import zeit.frontend.view_article
import zeit.frontend.view_centerpage
import zeit.frontend.view_gallery

def test_banner_channel_for_article(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    view = zeit.frontend.view_article.Article(context, mock.Mock())
    assert view.banner_channel == 'zeitmz/modeunddesign/article'

def test_banner_channel_for_gallery(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/galerien/fs-desktop-schreibtisch-computer')
    view = zeit.frontend.view_gallery.Gallery(context, mock.Mock())
    assert view.banner_channel == 'zeitmz/modeunddesign/article'

def test_banner_channel_for_longform(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    view = zeit.frontend.view_article.LongformArticle(context, mock.Mock())
    assert view.banner_channel == 'zeitmz/longform'

def test_banner_channel_for_feature_longform(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/feature/feature_longform')
    view = zeit.frontend.view_article.FeatureLongform(context, mock.Mock())
    assert view.banner_channel == 'gesellschaft/longform'

def test_banner_channel_for_centerpage(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/index')
    view = zeit.frontend.view_centerpage.Centerpage(context, mock.Mock())
    assert view.banner_channel == 'zeitmz/centerpage'
