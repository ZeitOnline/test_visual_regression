# -*- coding: utf-8 -*-
import mock

import zeit.cms.interfaces

import zeit.web.magazin.view_article
import zeit.web.magazin.view_centerpage
import zeit.web.magazin.view_gallery


def test_banner_channel_for_article(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/01')
    view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert view.banner_channel == 'zeitmz/modeunddesign/article'


def test_banner_channel_for_gallery(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/galerien/fs-desktop-schreibtisch-computer')
    view = zeit.web.magazin.view_gallery.Gallery(context, mock.Mock())
    assert view.banner_channel == 'zeitmz/leben/article'


def test_banner_channel_for_longform(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/05')
    view = zeit.web.magazin.view_article.LongformArticle(context, mock.Mock())
    assert view.banner_channel == 'zeitmz/longform'


def test_banner_channel_for_feature_longform(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/feature/feature_longform')
    view = zeit.web.magazin.view_article.FeatureLongform(context, mock.Mock())
    assert view.banner_channel == 'gesellschaft/longform'


def test_banner_channel_for_centerpage(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/centerpage/index')
    view = zeit.web.magazin.view_centerpage.Centerpage(context, mock.Mock())
    assert view.banner_channel == 'zeitmz/centerpage'
