import datetime

import pytest
import zope.component

import zeit.cms.interfaces
import zeit.content.cp.interfaces

import zeit.web.core.centerpage
import zeit.web.core.utils
import zeit.web.site.module.search_form


@pytest.fixture
def search_form(application, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/suche/index')
    block = zeit.web.core.utils.find_block(
        context, module='search-form')
    return zeit.web.core.template.get_module(block)


@pytest.fixture
def search_area(application, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/suche/index')
    area = zeit.web.core.utils.find_block(
        context, attrib='area', kind='ranking')
    return zeit.web.core.centerpage.get_area(area)


def test_search_form_should_allow_empty_query(
        dummy_request, search_form):
    dummy_request.GET['q'] = ''
    assert search_form.query is None


def test_search_form_should_allow_valid_query_string(
        dummy_request, search_form):
    dummy_request.GET['q'] = 'pfannkuchen'
    assert search_form.query == 'pfannkuchen'


def test_search_form_should_allow_empty_type_setting(
        dummy_request, search_form):
    dummy_request.GET['type'] = ''
    assert search_form.types == ['article', 'gallery', 'video']


def test_search_form_should_filter_type_settings(
        dummy_request, search_form):
    dummy_request.GET.add('type', 'article')
    dummy_request.GET.add('type', 'pfannkuchen')
    assert search_form.types == ['article']


def test_search_form_should_allow_empty_mode_setting(
        dummy_request, search_form):
    dummy_request.GET['mode'] = ''
    assert search_form.mode is None


def test_search_form_should_ignore_invalid_mode_setting(
        dummy_request, search_form):
    dummy_request.GET['mode'] = 'pfannkuchen'
    assert search_form.mode is None


def test_search_form_should_allow_valid_mode_setting(
        dummy_request, search_form):
    dummy_request.GET['mode'] = '1y'
    assert search_form.mode == '1y'


def test_search_form_should_default_to_recency_sort_order(
        dummy_request, search_form):
    dummy_request.GET['q'] = ''
    dummy_request.GET['sort'] = ''
    assert search_form.sort_order == 'aktuell'


def test_search_form_should_sort_valid_queries_by_relevancy(
        dummy_request, search_form):
    dummy_request.GET['q'] = 'pfannkuchen'
    dummy_request.GET['sort'] = ''
    assert search_form.sort_order == 'relevanz'


def test_search_form_should_ignore_invalid_sort_orders(
        dummy_request, search_form):
    dummy_request.GET['q'] = 'pfannkuchen'
    dummy_request.GET['sort'] = 'pfannkuchen'
    assert search_form.sort_order == 'relevanz'


def test_search_form_should_allow_valid_search_order_aktuell(
        dummy_request, search_form):
    dummy_request.GET['q'] = 'pfannkuchen'
    dummy_request.GET['sort'] = 'aktuell'
    assert search_form.sort_order == 'aktuell'


def test_search_form_should_allow_valid_search_order_relevanz(
        dummy_request, search_form):
    dummy_request.GET['q'] = 'pfannkuchen'
    dummy_request.GET['sort'] = 'relevanz'
    assert search_form.sort_order == 'relevanz'


def test_search_form_should_create_valid_empty_query_string(
        dummy_request, search_form):
    assert search_form.raw_query == (
        'type:(article OR gallery OR video) '
        'NOT product_id:(News OR afp OR SID OR ADV) '
        'NOT ressort:(Administratives OR News OR Aktuelles) '
        'NOT expires:[* TO NOW]')


def test_search_form_should_create_valid_fulltext_query_string(
        dummy_request, search_form):
    dummy_request.GET['q'] = 'pfannkuchen AND ahornsirup'
    assert search_form.raw_query == (
        '{!boost b=recip(ms(NOW,last-semantic-change),3.16e-11,1,1)}'
        '{!type=IntrafindQueryParser}(pfannkuchen AND ahornsirup) '
        'type:(article OR gallery OR video) '
        'NOT product_id:(News OR afp OR SID OR ADV) '
        'NOT ressort:(Administratives OR News OR Aktuelles) '
        'NOT expires:[* TO NOW]')


def test_search_form_should_create_valid_date_range_query_string(
        dummy_request, monkeypatch, search_form):
    def year_range():
        return datetime.datetime(2000, 1, 1), datetime.datetime(2010, 1, 1)

    monkeypatch.setattr(
        zeit.web.site.module.search_form, 'MODES', {'1y': (year_range,)})

    dummy_request.GET['mode'] = '1y'
    assert search_form.raw_query == (
        'last-semantic-change:[2000-01-01T00:00:00Z TO 2010-01-01T00:00:00Z] '
        'type:(article OR gallery OR video) '
        'NOT product_id:(News OR afp OR SID OR ADV) '
        'NOT ressort:(Administratives OR News OR Aktuelles) '
        'NOT expires:[* TO NOW]')


def test_search_form_should_create_valid_type_restricted_query(
        dummy_request, search_form):
    dummy_request.GET['mode'] = 'article gallery'
    assert search_form.raw_query == (
        'type:(article OR gallery OR video) '
        'NOT product_id:(News OR afp OR SID OR ADV) '
        'NOT ressort:(Administratives OR News OR Aktuelles) '
        'NOT expires:[* TO NOW]')


def test_search_area_should_produce_valid_set_of_search_results(search_area):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId': 'foo://zeit.de'}]
    assert list(search_area.values()[0])[0].uniqueId == 'foo://zeit.de'


def test_empty_search_result_should_produce_zero_hit_counter(search_area):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = []
    assert search_area.hits == 0


def test_successful_search_result_should_produce_nonzero_hit_counter(
        search_area):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId': 'http://xml.zeit.de/artikel/0%s' % i}
                    for i in range(1, 74)]
    assert search_area.hits == 73


def test_empty_search_result_should_produce_valid_resultset(search_area):
    assert len([a for b in search_area.values() for a in b if b]) == 0


def get_result_dict(unique_id):
    return {
        'date_last_published': '2015-07-01T09:50:42Z',
        'product_id': 'ZEI',
        'supertitle': 'Lorem ipsum',
        'title': 'Lorem ipsum',
        'uniqueId': unique_id}


def test_successful_search_result_should_produce_valid_resultset(search_area):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId': 'http://xml.zeit.de/artikel/0%s' % i}
                    for i in range(1, 9)]
    assert len([a for b in search_area.values() for a in b if b]) == 8
    solr.results = [{'uniqueId': 'http://xml.zeit.de/artikel/01'}]
    block = iter(search_area.values()).next()
    assert zeit.content.cp.interfaces.IAutomaticTeaserBlock.providedBy(block)
    assert zeit.cms.interfaces.ICMSContent.providedBy(iter(block).next())


def test_successful_search_result_should_render_in_browser(
        testbrowser, datasolr):
    browser = testbrowser('/suche/index')
    assert browser.cssselect('.cp-area--ranking .teaser-small')


def test_campus_print_article_has_correct_meta_line(
        testserver, selenium_driver):
    selenium_driver.get('{}/campus/article/simple_date_print'.format(
        testserver.url))
    date = selenium_driver.find_element_by_css_selector('.metadata__date')
    source = selenium_driver.find_element_by_css_selector('.metadata__source')

    assert date.text.strip() == (u'10. Januar 2016')
    assert source.text.strip() == u'DIE ZEIT Nr. 1/2015, 5. Mai 2015'


def test_campus_print_changed_article_has_correct_meta_line(
        testserver, selenium_driver):
    selenium_driver.get('{}/campus/article/simple_date_print_changed'.format(
        testserver.url))
    date = selenium_driver.find_element_by_css_selector('.metadata__date')
    source = selenium_driver.find_element_by_css_selector('.metadata__source')

    assert date.text.strip() == (u'10. Februar 2016, 10:39 Uhr /'
                                 u' Editiert am 22. Februar 2016, 18:18 Uhr')
    assert source.text.strip() == u'DIE ZEIT Nr. 5/2015, 29. Januar 2015'


def test_campus_changed_article_has_correct_meta_line(
        testserver, selenium_driver):
    selenium_driver.get('{}/campus/article/simple_date_changed'.format(
        testserver.url))
    date = selenium_driver.find_element_by_css_selector('.metadata__date')

    assert date.text.strip() == (u'10. Januar 2016, 10:39 Uhr /'
                                 u' Aktualisiert am 10. Februar '
                                 u'2016, 10:39 Uhr')


def test_campus_article_has_correct_meta_line(testserver, selenium_driver):
    selenium_driver.get('{}/campus/article/simple'.format(testserver.url))
    date = selenium_driver.find_element_by_css_selector('.metadata__date')

    assert date.text.strip() == (u'10. Januar 2016, 10:39 Uhr')
