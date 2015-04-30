import datetime

import pytest

import zeit.cms.interfaces

import zeit.web.site.search
import zeit.web.core.application


@pytest.fixture
def search_form(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/suche/index')
    return zeit.web.core.template.get_module(
        zeit.web.core.application.find_block(context, module='search-form'))


def test_search_form_should_allow_empty_query(search_form):
    search_form['q'] = None
    assert search_form.query is None


def test_search_form_should_allow_valid_query_string(search_form):
    search_form['q'] = 'pfannkuchen'
    assert search_form.query == 'pfannkuchen'


def test_search_form_should_allow_empty_type_setting(search_form):
    search_form['type'] = ''
    assert search_form.types == ['article', 'gallery', 'video']


def test_search_form_should_filter_type_settings(search_form):
    search_form['type'] = 'article pfannkuchen'
    assert search_form.types == ['article']


def test_search_form_should_allow_empty_mode_setting(search_form):
    search_form['mode'] = None
    assert search_form.mode is None


def test_search_form_should_ignore_invalid_mode_setting(search_form):
    search_form['mode'] = 'pfannkuchen'
    assert search_form.mode is None


def test_search_form_should_allow_valid_mode_setting(search_form):
    search_form['mode'] = '1y'
    assert search_form.mode == '1y'


def test_search_form_should_default_to_recency_sort_order(search_form):
    search_form['q'] = None
    search_form['sort'] = None
    assert search_form.sort_order == 'aktuell'


def test_search_form_should_sort_valid_queries_by_relevancy(search_form):
    search_form['q'] = 'pfannkuchen'
    search_form['sort'] = None
    assert search_form.sort_order == 'relevanz'


def test_search_form_should_ignore_invalid_sort_orders(search_form):
    search_form['q'] = 'pfannkuchen'
    search_form['sort'] = 'pfannkuchen'
    assert search_form.sort_order == 'relevanz'


def test_search_form_should_allow_valid_valid_search_orders(search_form):
    search_form['q'] = 'pfannkuchen'
    search_form['sort'] = 'aktuell'
    assert search_form.sort_order == 'aktuell'


def test_search_form_should_ignore_negative_page_numbers(search_form):
    search_form['page'] = '-73'
    assert search_form.page == 73


def test_search_form_should_allow_allow_valid_page_numbers(search_form):
    search_form['page'] = '42'
    assert search_form.page == 42


def test_search_form_should_ignore_invalid_page_numbers(search_form):
    search_form['page'] = 'pfannkuchen'
    assert search_form.page == 1


def test_search_form_should_create_valid_empty_query_string(search_form):
    assert search_form.raw_query == (
        'type:(article OR gallery OR video) NOT expires:[* TO NOW] NOT '
        'product_id:(News OR afp OR SID OR ADV) NOT ressort:(Administratives '
        'OR News OR Aktuelles)')


def test_search_form_should_create_valid_fulltext_query_string(search_form):
    search_form['q'] = 'pfannkuchen AND ahornsirup'
    assert search_form.raw_query == (
        '{!boost b=recip(ms(NOW,last-semantic-change),3.16e-11,1,1)}'
        '{!type=IntrafindQueryParser}(pfannkuchen AND ahornsirup) type:'
        '(article OR gallery OR video) NOT expires:[* TO NOW] NOT product_id:'
        '(News OR afp OR SID OR ADV) NOT ressort:(Administratives OR News OR '
        'Aktuelles)')


def test_search_form_should_create_valid_date_range_query_string(
        monkeypatch, search_form):
    def year_range():
        return datetime.datetime(2000, 1, 1), datetime.datetime(2010, 1, 1)

    monkeypatch.setattr(
        zeit.web.site.search, 'MODES', {'1y': (year_range,)})

    search_form['mode'] = '1y'
    assert search_form.raw_query == (
        'last-semantic-change:[2000-01-01T00:00:00Z TO 2010-01-01T00:00:00Z] '
        'type:(article OR gallery OR video) NOT expires:[* TO NOW] NOT '
        'product_id:(News OR afp OR SID OR ADV) NOT ressort:(Administratives '
        'OR News OR Aktuelles)')


def test_search_form_should_create_valid_type_restricted_query(search_form):
    search_form['mode'] = 'article gallery'
    assert search_form.raw_query == (
        'type:(article OR gallery OR video) NOT expires:[* TO NOW] NOT '
        'product_id:(News OR afp OR SID OR ADV) NOT ressort:(Administratives '
        'OR News OR Aktuelles)')
