# -*- coding: utf-8 -*-

import mock
import pytest

import zeit.cms.interfaces

import zeit.web.core.byline


def test_article_byline_should_be_represented_as_a_nested_tuple(application):
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


def test_quiz_byline_should_be_represented_as_a_nested_tuple(application):
    quiz = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/quiz/quiz-workaholic')
    byline = zeit.web.core.byline.get_byline(quiz)
    assert byline.context == quiz
    assert byline == [
        ('text', u'Von'),
        ('enum', (
            ('text', u'Nicole Sagener'),))]


@pytest.fixture(scope='function')
def fake_article():
    article = mock.Mock()
    article.authorships = []
    article.authors = ['Shakespeare']
    article.serie = None
    article.genre = None
    return article


def test_byline_should_have_genres_if_provided(application, fake_article):
    fake_article.genre = 'glosse'
    byline = zeit.web.core.byline.Byline(fake_article)
    assert byline[0] == ('text', u'Eine Glosse von')

    fake_article.genre = 'kommentar'
    byline = zeit.web.core.byline.Byline(fake_article)
    assert byline[0] == ('text', u'Ein Kommentar von')


def test_some_byline_genres_should_not_be_displayed(application, fake_article):
    fake_article.genre = 'nachricht'
    byline = zeit.web.core.byline.Byline(fake_article)
    assert byline[0] == ('text', 'Von')


def test_byline_should_handle_interview_exception(application, fake_article):
    fake_article.genre = 'interview'
    byline = zeit.web.core.byline.Byline(fake_article)
    assert byline[0] == ('text', u'Interview:')


def test_byline_should_handle_column_exception(application, fake_article):
    fake_article.genre = 'interview'
    fake_article.serie = mock.Mock()
    fake_article.serie.column = True
    byline = zeit.web.core.byline.Byline(fake_article)
    assert byline[0] == ('text', u'Eine Kolumne von')


def test_byline_should_be_empty_if_no_authors_given(application, fake_article):
    fake_article.genre = 'interview'
    fake_article.authorships = [None]
    fake_article.authors = [None]
    byline = zeit.web.core.byline.Byline(fake_article)
    assert len(byline) == 0


def test_teaser_byline_should_expand_authors_as_text(monkeypatch):
    author = mock.Mock()
    author.target.display_name = u'Max Mustermann'
    author2 = mock.Mock()
    author2.target.display_name = u'Anne Mustermann'
    cls = zeit.web.core.byline.Byline
    monkeypatch.setattr(cls, '__init__', lambda s: list.__init__(s))
    assert tuple(cls().expand_authors([author, author2])) == (
        ('text', u'Max Mustermann'), ('text', u'Anne Mustermann'))


def test_teaser_byline_should_ignore_authors_without_display_name(monkeypatch):
    author = mock.Mock()
    author.target = mock.Mock(spec=[])
    cls = zeit.web.core.byline.Byline
    monkeypatch.setattr(cls, '__init__', lambda s: list.__init__(s))
    assert tuple(cls().expand_authors([author])) == ()


def test_content_byline_should_expand_authors_with_links(monkeypatch):
    author = mock.Mock()
    author.target.display_name = u'Max Mustermann'
    author.target.uniqueId = u'http://max'
    author2 = mock.Mock()
    author2.target.display_name = u'Anne Mustermann'
    author2.target.uniqueId = None
    cls = zeit.web.core.byline.ArticleByline
    monkeypatch.setattr(cls, '__init__', lambda s: list.__init__(s))
    assert tuple(cls().expand_authors([author, author2])) == (
        ('linked_author', author.target), ('plain_author', author2.target))


def test_one_author_should_be_in_byline(application, fake_article):
    author = mock.Mock()
    author.target.display_name = u'Max Mustermann'
    author.target.uniqueId = u'http://authör'
    author.location = u'Bimbachtal'
    fake_article.authorships = [author]
    byline = zeit.web.core.byline.Byline(fake_article)
    assert list(byline) == [
        ('text', ('Von')),
        ('csv', (
            ('enum', (
                ('text', u'Max Mustermann'),)),
            ('text', u'Bimbachtal')))]


def test_two_authors_should_be_in_byline(application, fake_article):
    author = mock.Mock()
    author.target.display_name = u'Max Mustermann'
    author.target.uniqueId = u'http://authör'
    author.location = u'Bimbachtal'
    author2 = mock.Mock()
    author2.target.display_name = u'Anne Mustermann'
    author2.target.uniqueId = u'http://author2'
    author2.location = u'Bimbachtal'

    fake_article.authorships = [author, author2]
    byline = zeit.web.core.byline.Byline(fake_article)
    assert list(byline) == [
        ('text', ('Von')),
        ('csv', (
            ('enum', (
                ('text', u'Max Mustermann'),
                ('text', u'Anne Mustermann'))),
            ('text', u'Bimbachtal')))]


def test_no_locations_should_be_in_byline_if_not_provided(
        application, fake_article):
    author = mock.Mock()
    author.target.display_name = u'Max Mustermann'
    author.target.uniqueId = u'http://authör'
    author.location = None
    author2 = mock.Mock()
    author2.target.display_name = u'Anne Mustermann'
    author2.target.uniqueId = u'http://author2'
    author2.location = None

    fake_article.authorships = [author, author2]
    byline = zeit.web.core.byline.Byline(fake_article)
    assert list(byline) == [
        ('text', ('Von')),
        ('enum', (
            ('text', u'Max Mustermann'),
            ('text', u'Anne Mustermann')))]


def test_three_authors_should_be_in_byline(application, fake_article):
    author = mock.Mock()
    author.target.display_name = u'Max Mustermann'
    author.target.uniqueId = u'http://authör'
    author.location = u'Bimbachtal'
    author2 = mock.Mock()
    author2.target.display_name = u'Anne Mustermann'
    author2.target.uniqueId = u'http://author2'
    author2.location = u'Bimbachtal'
    author3 = mock.Mock()
    author3.target.display_name = u'Ernst Ärgerlich'
    author3.target.uniqueId = u'http://author3'
    author3.location = u'Bimbachtal'

    fake_article.authorships = [author, author2, author3]
    byline = zeit.web.core.byline.Byline(fake_article)
    assert list(byline) == [
        ('text', ('Von')),
        ('csv', (
            ('enum', (
                ('text', u'Max Mustermann'),
                ('text', u'Anne Mustermann'),
                ('text', u'Ernst Ärgerlich'))),
            ('text', u'Bimbachtal')))]


def test_locations_none_b_b_authors_should_be_in_byline(
        application, fake_article):
    author = mock.Mock()
    author.target.display_name = u'Max Mustermann'
    author.target.uniqueId = u'http://authör'
    author.location = None
    author2 = mock.Mock()
    author2.target.display_name = u'Anne Mustermann'
    author2.target.uniqueId = u'http://author2'
    author2.location = u'Bimbachtal'
    author3 = mock.Mock()
    author3.target.display_name = u'Ernst Ärgerlich'
    author3.target.uniqueId = u'http://author3'
    author3.location = u'Bimbachtal'

    fake_article.authorships = [author, author2, author3]
    byline = zeit.web.core.byline.Byline(fake_article)
    assert list(byline) == [
        ('text', ('Von')),
        ('enum', (
            ('enum', (
                ('text', u'Max Mustermann'),)),
            ('csv', (
                ('enum', (
                    ('text', u'Anne Mustermann'),
                    ('text', u'Ernst Ärgerlich'))),
                ('text', u'Bimbachtal')))))]


def test_locations_a_a_a_should_produce_correct_list(
        application, fake_article):
    author = mock.Mock()
    author.target.display_name = u'Max Mustermann'
    author.target.uniqueId = u'http://authör'
    author.location = u'Hørsholm'
    author2 = mock.Mock()
    author2.target.display_name = u'Anne Mustermann'
    author2.target.uniqueId = u'http://author2'
    author2.location = u'Hørsholm'
    author3 = mock.Mock()
    author3.target.display_name = u'Ernst Ärgerlich'
    author3.target.uniqueId = u'http://author3'
    author3.location = u'Hørsholm'

    fake_article.authorships = [author, author2, author3]
    byline = zeit.web.core.byline.Byline(fake_article)
    assert list(byline) == [
        ('text', ('Von')),
        ('csv', (
            ('enum', (
                ('text', u'Max Mustermann'),
                ('text', u'Anne Mustermann'),
                ('text', u'Ernst Ärgerlich'))),
            ('text', u'Hørsholm')))]


def test_locations_a_b_a_should_produce_correct_list(
        application, fake_article):
    author = mock.Mock()
    author.target.display_name = u'Max Mustermann'
    author.target.uniqueId = u'http://authör'
    author.location = u'Hørsholm'
    author2 = mock.Mock()
    author2.target.display_name = u'Anne Mustermann'
    author2.target.uniqueId = u'http://author2'
    author2.location = u'Bimbachtal'
    author3 = mock.Mock()
    author3.target.display_name = u'Ernst Ärgerlich'
    author3.target.uniqueId = u'http://author3'
    author3.location = u'Hørsholm'

    fake_article.authorships = [author, author2, author3]
    byline = zeit.web.core.byline.Byline(fake_article)
    assert list(byline) == [
        ('text', ('Von')),
        ('enum', (
            ('csv', (
                ('enum', (
                    ('text', u'Anne Mustermann'),)),
                ('text', u'Bimbachtal'))),
            ('csv', (
                ('enum', (
                    ('text', u'Max Mustermann'),
                    ('text', u'Ernst Ärgerlich'))),
                ('text', u'Hørsholm')))))]


def test_locations_b_b_a_should_produce_correct_list(
        application, fake_article):
    author = mock.Mock()
    author.target.display_name = u'Max Mustermann'
    author.target.uniqueId = u'http://authör'
    author.location = u'Bimbachtal'
    author2 = mock.Mock()
    author2.target.display_name = u'Anne Mustermann'
    author2.target.uniqueId = u'http://author2'
    author2.location = u'Bimbachtal'
    author3 = mock.Mock()
    author3.target.display_name = u'Ernst Ärgerlich'
    author3.target.uniqueId = u'http://author3'
    author3.location = u'Hørsholm'

    fake_article.authorships = [author, author2, author3]
    byline = zeit.web.core.byline.Byline(fake_article)
    assert list(byline) == [
        ('text', ('Von')),
        ('enum', (
            ('csv', (
                ('enum', (
                    ('text', u'Max Mustermann'),
                    ('text', u'Anne Mustermann'))),
                ('text', u'Bimbachtal'))),
            ('csv', (
                ('enum', (
                    ('text', u'Ernst Ärgerlich'),)),
                ('text', u'Hørsholm')))))]
