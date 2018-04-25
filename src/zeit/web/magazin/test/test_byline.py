# -*- coding: utf-8 -*-

import zeit.cms.interfaces

import zeit.web.core.byline


def test_article_byline_for_column(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/08')
    byline = zeit.web.core.byline.get_byline(article)
    assert byline.context == article
    assert byline == [
        ('text', u'Ein Kommentar von'),
        ('enum', (
            ('csv', (
                ('enum', (
                    ('text', u'Anne Mustermann'),)),
                ('text', u'Berlin'))),
            ('csv', (
                ('enum', (
                    ('text', u'Oliver Fritsch'),)),
                ('text', u'London')))))]


def test_article_byline_for_glosse(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/09')
    byline = zeit.web.core.byline.get_byline(article)
    assert byline.context == article
    assert byline == [
        ('text', u'Eine Glosse von'),
        ('enum', (
            ('text', u'Anne Mustermann'),))]


def test_article_byline_without_genre(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/05')
    byline = zeit.web.core.byline.get_byline(article)
    assert byline.context == article
    assert byline == [
        ('text', u'Von'),
        ('enum', (
            ('text', u'Anne Mustermann'),))]
