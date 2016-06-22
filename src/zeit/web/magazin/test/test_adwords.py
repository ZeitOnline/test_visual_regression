# -*- coding: utf-8 -*-
import datetime

import babel.dates
import mock

import zeit.cms.interfaces

import zeit.web.magazin.view_article
import zeit.web.magazin.view_centerpage


def test_adwords_for_article(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/01')
    view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    adwords = ','.join(view.adwords)
    assert adwords == 'zeitonline,zeitmz'


def test_adwords_for_lead_article(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/01')
    view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    tz = babel.dates.get_timezone('Europe/Berlin')
    today = datetime.datetime.now(tz)
    view.leadtime = mock.Mock()
    view.leadtime.start = today
    adwords = ','.join(view.adwords)
    assert adwords == 'zeitonline,zeitmz,ToM'


def test_adwords_for_longform(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/05')
    view = zeit.web.magazin.view_article.LongformArticle(context, mock.Mock())
    adwords = ','.join(view.adwords)
    assert adwords == 'zeitonline,zeitmz,longform,noiqdband'


def test_adwords_for_feature_longform(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/feature/feature_longform')
    view = zeit.web.magazin.view_article.FeatureLongform(context, mock.Mock())
    adwords = ','.join(view.adwords)
    assert adwords == 'zeitonline,longform,noiqdband'


def test_adwords_for_centerpage(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/centerpage/index')
    view = zeit.web.magazin.view_centerpage.Centerpage(context, mock.Mock())
    adwords = ','.join(view.adwords)
    assert adwords == 'zeitonline,zeitmz'
