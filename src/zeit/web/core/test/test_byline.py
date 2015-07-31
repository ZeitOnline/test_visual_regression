# -*- coding: utf-8 -*-

import mock
import pytest

import zeit.cms.interfaces

import zeit.web.core.byline


def test_article_byline_should_be_represented_as_a_nested_tuple(application):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/08')
    byline = zeit.web.core.byline.ITeaserByline(article)
    assert byline.context == article
    assert byline == [
        ('text', u'Ein Kommentar'),
        ('text', u'von'),
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
        'http://xml.zeit.de/quiz/quiz-workaholic')
    byline = zeit.web.core.byline.ITeaserByline(quiz)
    assert byline.context == quiz
    assert byline == [
        ('text', u'Von'),
        ('enum', (
            ('text', u'Nicole Sagener'),))]


@pytest.fixture(scope='function')
def patched_byline(request, monkeypatch):
    def init(self, context):
        list.__init__(self)
        self.context = context
    monkeypatch.setattr(zeit.web.core.byline.Byline, '__init__', init)
    return zeit.web.core.byline.Byline


def test_byline_should_have_genres_if_provided(patched_byline):
    context = mock.Mock()
    context.genre = 'glosse'
    byline = patched_byline(context)
    byline.genre()
    assert byline[0] == ('text', u'Eine Glosse')

    context.genre = 'kommentar'
    byline = patched_byline(context)
    byline.genre()
    assert byline[0] == ('text', u'Ein Kommentar')


def test_some_byline_genres_should_not_be_displayed(patched_byline):
    context = mock.Mock()
    context.genre = 'nachricht'
    byline = patched_byline(context)
    byline.genre()
    assert len(byline) == 0


def test_byline_should_have_von_or_von(patched_byline):
    context = mock.Mock()
    byline = patched_byline(context)
    byline.from_()
    assert byline[0] == ('text', u'Von')

    byline.from_()
    assert byline[1] == ('text', u'von')


def test_byline_should_handle_interview_exception(patched_byline):
    context = mock.Mock()
    context.genre = 'interview'
    byline = patched_byline(context)
    byline.append(('text', u'foo'))
    byline.interview()
    assert byline[0] == ('text', u'Interview:')


def test_byline_should_be_empty_if_no_authors_given(patched_byline):
    context = mock.Mock()
    context.authorships = [None]
    context.authors = [None]
    byline = patched_byline(context)
    byline.append(('text', u'foo'))
    byline.groups()
    assert len(byline) == 0


def test_teaser_byline_should_expand_authors_as_text(monkeypatch):
    author = mock.Mock()
    author.target.display_name = u'Max Mustermann'
    author2 = mock.Mock()
    author2.target.display_name = u'Anne Mustermann'
    cls = zeit.web.core.byline.TeaserByline
    monkeypatch.setattr(cls, '__init__', lambda s: list.__init__(s))
    assert tuple(cls().expand_authors([author, author2])) == (
        ('text', u'Max Mustermann'), ('text', u'Anne Mustermann'))


def test_content_byline_should_expand_authors_with_links(monkeypatch):
    author = mock.Mock()
    author.target.display_name = u'Max Mustermann'
    author.target.uniqueId = u'http://max'
    author2 = mock.Mock()
    author2.target.display_name = u'Anne Mustermann'
    author2.target.uniqueId = None
    cls = zeit.web.core.byline.ArticleContentByline
    monkeypatch.setattr(cls, '__init__', lambda s: list.__init__(s))
    assert tuple(cls().expand_authors([author, author2])) == (
        ('linked_author', author.target), ('plain_author', author2.target))


def test_one_author_should_be_in_byline(patched_byline):
    context = mock.Mock()
    author = mock.Mock()
    author.target.display_name = u'Max Mustermann'
    author.target.uniqueId = u'http://authör'
    author.location = u'Bimbachtal'
    context.authorships = [author]
    byline = patched_byline(context)
    byline.groups()
    assert byline == [
        ('csv', (
            ('enum', (
                ('text', u'Max Mustermann'),)),
            ('text', u'Bimbachtal')))]


def test_two_authors_should_be_in_byline(patched_byline):
    context = mock.Mock()
    author = mock.Mock()
    author.target.display_name = u'Max Mustermann'
    author.target.uniqueId = u'http://authör'
    author.location = u'Bimbachtal'
    author2 = mock.Mock()
    author2.target.display_name = u'Anne Mustermann'
    author2.target.uniqueId = u'http://author2'
    author2.location = u'Bimbachtal'

    context.authorships = [author, author2]
    byline = patched_byline(context)
    byline.groups()
    assert byline == [
        ('csv', (
            ('enum', (
                ('text', u'Max Mustermann'),
                ('text', u'Anne Mustermann'))),
            ('text', u'Bimbachtal')))]


def test_no_locations_should_be_in_byline_if_not_provided(patched_byline):
    context = mock.Mock()
    author = mock.Mock()
    author.target.display_name = u'Max Mustermann'
    author.target.uniqueId = u'http://authör'
    author.location = None
    author2 = mock.Mock()
    author2.target.display_name = u'Anne Mustermann'
    author2.target.uniqueId = u'http://author2'
    author2.location = None

    context.authorships = [author, author2]
    byline = patched_byline(context)
    byline.groups()
    assert byline == [
        ('enum', (
            ('text', u'Max Mustermann'),
            ('text', u'Anne Mustermann')))]


def test_three_authors_should_be_in_byline(patched_byline):
    context = mock.Mock()
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

    context.authorships = [author, author2, author3]
    byline = patched_byline(context)
    byline.groups()
    assert byline == [
        ('csv', (
            ('enum', (
                ('text', u'Max Mustermann'),
                ('text', u'Anne Mustermann'),
                ('text', u'Ernst Ärgerlich'))),
            ('text', u'Bimbachtal')))]


def test_locations_none_b_b_authors_should_be_in_byline(patched_byline):
    context = mock.Mock()
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

    context.authorships = [author, author2, author3]
    byline = patched_byline(context)
    byline.groups()
    assert byline == [
        ('enum', (
            ('enum', (
                ('text', u'Max Mustermann'),)),
            ('csv', (
                ('enum', (
                    ('text', u'Anne Mustermann'),
                    ('text', u'Ernst Ärgerlich'))),
                ('text', u'Bimbachtal')))))]


def test_locations_a_a_a_should_produce_correct_list(patched_byline):
    context = mock.Mock()
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

    context.authorships = [author, author2, author3]
    byline = patched_byline(context)
    byline.groups()
    assert byline == [
        ('csv', (
            ('enum', (
                ('text', u'Max Mustermann'),
                ('text', u'Anne Mustermann'),
                ('text', u'Ernst Ärgerlich'))),
            ('text', u'Hørsholm')))]


def test_locations_a_b_a_should_produce_correct_list(patched_byline):
    context = mock.Mock()
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

    context.authorships = [author, author2, author3]
    byline = patched_byline(context)
    byline.groups()
    assert byline == [
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


def test_locations_b_b_a_should_produce_correct_list(patched_byline):
    context = mock.Mock()
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

    context.authorships = [author, author2, author3]
    byline = patched_byline(context)
    byline.groups()
    assert byline == [
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
