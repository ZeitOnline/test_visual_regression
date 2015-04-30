import pytest

import zeit.cms.interfaces

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
