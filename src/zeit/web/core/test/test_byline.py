# -*- coding: utf-8 -*-

import mock
import pytest

import zeit.cms.interfaces

import zeit.web.core.byline


def test_byline_should_be_represented_by_a_string(application):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/08')
    byline = zeit.web.core.byline.IRenderByline(article)
    assert unicode(byline) == ('Ein Kommentar von Anne Mustermann, '
                               'Berlin und Oliver Fritsch, London')


@pytest.fixture(scope='function')
def patched_byline(request, monkeypatch):
    def init(self):
        self.byline = []
    monkeypatch.setattr(zeit.web.core.byline.RenderByline, '__init__', init)
    return zeit.web.core.byline.RenderByline


def test_byline_should_have_genres_if_provided(patched_byline):
    byline = patched_byline()

    content = mock.Mock()
    content.genre = 'glosse'
    content.title = lambda x: 'glosse'
    byline._genre(content)
    assert unicode(byline) == 'Eine Glosse '


def test_some_byline_genres_should_not_be_displayed(patched_byline):
    byline = patched_byline()
    content = mock.Mock()
    content.genre = 'nachricht'
    byline._genre(content)
    assert unicode(byline) == ''


def test_byline_should_have_von_or_Von(patched_byline):
    byline = patched_byline()
    content = mock.Mock()

    byline._von(content)
    assert byline.byline == ['Von ']

    byline.byline = ['not empty']
    byline._von(content)
    assert byline.byline[1] == 'von '


def test_byline_should_have_interview_exception(patched_byline):
    byline = patched_byline()
    content = mock.Mock()
    content.genre = 'interview'
    content.title = lambda x: 'Interview'
    byline._interview_exception(content)
    assert unicode(byline) == 'Interview: '


def test_byline_should_be_empty_if_no_authors_given(patched_byline):
    byline = patched_byline()
    content = mock.Mock()
    content.authorships = [None]
    byline.byline = ['full']
    byline._author_str(content)
    assert not byline.byline


def test_one_author_should_be_in_byline(patched_byline):
    byline = patched_byline()
    content = mock.Mock()
    author = mock.Mock()
    author.target.display_name = 'Max Mustermann'
    author.target.uniqueId = 'http://author'
    author.location = 'Berlin'
    content.authorships = [author]
    byline._author_str(content)
    assert unicode(byline) == 'Max Mustermann, Berlin'


def test_two_authors_should_be_in_byline(patched_byline):
    byline = patched_byline()
    content = mock.Mock()
    author = mock.Mock()
    author.target.display_name = 'Max Mustermann'
    author.target.uniqueId = 'http://author'
    author.location = 'Berlin'
    author2 = mock.Mock()
    author2.target.display_name = 'Anne Mustermann'
    author2.target.uniqueId = 'http://author2'
    author2.location = 'Berlin'

    content.authorships = [author, author2]
    byline._author_str(content)
    assert unicode(byline) == (u'Max Mustermann und Anne Mustermann, Berlin')


def test_no_locations_should_be_in_byline_if_not_provided(patched_byline):
    byline = patched_byline()
    content = mock.Mock()
    author = mock.Mock()
    author.target.display_name = 'Max Mustermann'
    author.target.uniqueId = 'http://author'
    author.location = None
    author2 = mock.Mock()
    author2.target.display_name = 'Anne Mustermann'
    author2.target.uniqueId = 'http://author2'
    author2.location = None

    content.authorships = [author, author2]
    byline._author_str(content)
    assert unicode(byline) == (u'Max Mustermann und Anne Mustermann')


def test_three_authors_should_be_in_byline(patched_byline):
    byline = patched_byline()
    content = mock.Mock()
    author = mock.Mock()
    author.target.display_name = 'Max Mustermann'
    author.target.uniqueId = 'http://author'
    author.location = 'Berlin'
    author2 = mock.Mock()
    author2.target.display_name = 'Anne Mustermann'
    author2.target.uniqueId = 'http://author2'
    author2.location = 'Berlin'
    author3 = mock.Mock()
    author3.target.display_name = u'Ernst Ärgerlich'
    author3.target.uniqueId = 'http://author3'
    author3.location = 'Berlin'

    content.authorships = [author, author2, author3]
    byline._author_str(content)
    assert unicode(byline) == (u'Max Mustermann, Anne Mustermann und '
                               u'Ernst Ärgerlich, Berlin')


def test_locations_none_b_b_authors_should_be_in_byline(patched_byline):
    byline = patched_byline()
    content = mock.Mock()
    author = mock.Mock()
    author.target.display_name = 'Max Mustermann'
    author.target.uniqueId = 'http://author'
    author.location = None
    author2 = mock.Mock()
    author2.target.display_name = 'Anne Mustermann'
    author2.target.uniqueId = 'http://author2'
    author2.location = 'Berlin'
    author3 = mock.Mock()
    author3.target.display_name = u'Ernst Ärgerlich'
    author3.target.uniqueId = 'http://author3'
    author3.location = 'Berlin'

    content.authorships = [author, author2, author3]
    authors = filter(lambda a: a is not None, content.authorships)
    authors, locations = byline._author_location_list(authors)
    assert locations == ['', ', Berlin', ', Berlin']


def test_locations_a_a_a_should_produce_correct_list(patched_byline):
    byline = patched_byline()
    content = mock.Mock()
    author = mock.Mock()
    author.target.display_name = 'Max Mustermann'
    author.target.uniqueId = 'http://author'
    author.location = 'Hamburg'
    author2 = mock.Mock()
    author2.target.display_name = 'Anne Mustermann'
    author2.target.uniqueId = 'http://author2'
    author2.location = 'Hamburg'
    author3 = mock.Mock()
    author3.target.display_name = 'Ernst Ärgerlich'
    author3.target.uniqueId = 'http://author3'
    author3.location = 'Hamburg'

    content.authorships = [author, author2, author3]
    authors = filter(lambda a: a is not None, content.authorships)
    authors, locations = byline._author_location_list(authors)
    assert locations == ['', '', ', Hamburg']


def test_locations_a_b_a_should_produce_correct_list(patched_byline):
    byline = patched_byline()
    content = mock.Mock()
    author = mock.Mock()
    author.target.display_name = 'Max Mustermann'
    author.target.uniqueId = 'http://author'
    author.location = 'Hamburg'
    author2 = mock.Mock()
    author2.target.display_name = 'Anne Mustermann'
    author2.target.uniqueId = 'http://author2'
    author2.location = 'Berlin'
    author3 = mock.Mock()
    author3.target.display_name = 'Ernst Ärgerlich'
    author3.target.uniqueId = 'http://author3'
    author3.location = 'Hamburg'

    content.authorships = [author, author2, author3]
    authors = filter(lambda a: a is not None, content.authorships)
    authors, locations = byline._author_location_list(authors)
    assert locations == [', Hamburg', ', Berlin', ', Hamburg']


def test_locations_b_b_a_should_produce_correct_list(patched_byline):
    byline = patched_byline()
    content = mock.Mock()
    author = mock.Mock()
    author.target.display_name = 'Max Mustermann'
    author.target.uniqueId = 'http://author'
    author.location = 'Berlin'
    author2 = mock.Mock()
    author2.target.display_name = 'Anne Mustermann'
    author2.target.uniqueId = 'http://author2'
    author2.location = 'Berlin'
    author3 = mock.Mock()
    author3.target.display_name = 'Ernst Ärgerlich'
    author3.target.uniqueId = 'http://author3'
    author3.location = 'Hamburg'

    content.authorships = [author, author2, author3]
    authors = filter(lambda a: a is not None, content.authorships)
    authors, locations = byline._author_location_list(authors)
    assert locations == [', Berlin', ', Berlin', ', Hamburg']
