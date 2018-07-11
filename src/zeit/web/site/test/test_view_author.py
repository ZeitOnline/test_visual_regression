# -*- coding: utf-8 -*-
import datetime

import lxml.html
import mock
import pyramid.testing
import zope.component

import zeit.retresco.interfaces

import zeit.web.core.interfaces


def test_author_page_contains_main_navigation(testbrowser):
    browser = testbrowser('/autoren/j_random')
    header = browser.cssselect('header.header')[0]
    assert header.cssselect('.nav')
    assert header.cssselect('.nav__ressorts')


def test_author_header_should_be_fully_rendered(testbrowser):
    browser = testbrowser('/autoren/j_random')
    name = browser.cssselect('.author-header__name')
    summary = browser.cssselect('.author-header__summary')
    image = browser.cssselect('.author-header__image')

    assert len(name) == 1
    assert len(summary) == 1
    assert len(image) == 1
    assert 'J. Random Hacker' in name[0].text
    assert 'Random Hacker ist Redakteur' in summary[0].text


def test_author_page_should_show_favourite_content_if_available(testbrowser):
    browser = testbrowser('/autoren/j_random')
    assert len(browser.cssselect(
        '.cp-area--author-favourite-content .teaser-small')) == 3


def test_author_page_should_hide_favourite_content_if_missing(testbrowser):
    browser = testbrowser('/autoren/anne_mustermann')
    assert len(browser.cssselect('.cp-area--author-favourite-content')) == 0
    assert len(browser.cssselect('.teaser-small')) == 0


def test_author_page_contains_required_structured_data(testbrowser):
    data = testbrowser('/autoren/W/Jochen_Wegner/index').structured_data()

    author = data['Person']

    assert author['mainEntityOfPage']['@id'] == (
        'http://localhost/autoren/W/Jochen_Wegner/index')
    assert author['name'] == 'Jochen Wegner'
    assert author['jobTitle'] == 'Chefredakteur, ZEIT ONLINE.'
    assert author['description']
    assert author['image']['url'] == (
        'http://localhost/autoren/W/Jochen_Wegner/jochen-wegner/'
        'square__900x900')
    assert author['image']['width'] == 900
    assert author['image']['height'] == 900
    assert len(author['sameAs']) == 3
    assert author['url'] == 'http://localhost/autoren/W/Jochen_Wegner/index'


def test_author_page_should_show_articles_by_author(testbrowser):
    es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    es.results = [
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/01'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/02'}]
    browser = testbrowser('/autoren/anne_mustermann')
    assert len(browser.cssselect('.teaser-small')) == 2


def test_articles_by_author_should_paginate(testbrowser):
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    settings['author_articles_page_size'] = 1
    es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    es.results = [
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/01'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/02'}]
    browser = testbrowser('/autoren/anne_mustermann?p=2')
    assert len(browser.cssselect('.teaser-small')) == 1
    page = browser.cssselect('.pager__page--current')[0]
    assert page.text_content().strip() == '2'


def test_author_area_articles_should_offset_correctly(
        application, dummy_request):

    author = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/autoren/j_random')
    area = zeit.web.site.view_author.create_author_article_area(author)

    dummy_request.GET['p'] = '4'
    area.request = dummy_request

    assert area.surrounding_teasers == 3
    assert area.count == 10
    assert area.start == 27


def test_author_page_with_favourite_content_should_get_total_pages_correctly(
        testbrowser):
    es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    # case 1: 7 articles on page 1, 10 articles on page 2
    es.results = ([{'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/01'}
                   for i in range(17)])
    select = testbrowser('/autoren/j_random').cssselect
    assert len(select('.cp-area--author-favourite-content article')) == 3
    assert len(select('.pager__pages .pager__page')) == 2

    # case 2: 7 articles on page 1, 10 articles on page 2, 1 article on page 3
    es.results = ([{'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/01'}
                   for i in range(18)])
    select = testbrowser('/autoren/j_random').cssselect
    assert len(select('.cp-area--author-favourite-content article')) == 3
    assert len(select('.pager__pages .pager__page')) == 3


def test_author_page_should_hide_favourite_content_on_further_pages(
        testbrowser):
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    settings['author_articles_page_size'] = 4
    es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    es.results = [
        {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/01'},
        {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/02'},
        {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/03'},
        {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/04'},
        {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/05'},
        {'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/06'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/01'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/02'}]
    # we have 8 solr hits + 3 favorite articles
    # we expect 3 pages, considering page_size = 4
    # page 1: 3 favorites + 1 more, adds up to 4
    # page 2: 4 articles - should be result no. 2-5
    # page 3: the remaining 3 articles - result no. 6-8
    select = testbrowser('/autoren/j_random').cssselect
    assert len(select('.cp-area--author-favourite-content')) == 1
    assert len(select('.cp-area--author-favourite-content article')) == 3
    assert len(select('.cp-area--author-articles article')) == 1
    assert len(select('.teaser-small')) == 4
    assert len(select('.pager__pages .pager__page')) == 3
    select = testbrowser('/autoren/j_random?p=2').cssselect
    assert len(select('.cp-area--author-favourite-content')) == 0
    assert len(select('.teaser-small')) == 4
    select = testbrowser('/autoren/j_random?p=3').cssselect
    assert len(select('.teaser-small')) == 3


def test_articles_by_author_should_not_repeat_favourite_content(
        testbrowser, monkeypatch):
    author = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/autoren/j_random')
    es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    mock_search = mock.Mock()
    monkeypatch.setattr(es, 'search', mock_search)
    testbrowser('/autoren/j_random')
    for fav in author.favourite_content:
        assert (zeit.cms.content.interfaces.IUUID(fav).id in
                mock_search.call_args[0][0]['query']['bool']['must_not']
                ['ids']['values'])


def test_first_page_shows_fewer_solr_results_since_it_shows_favourite_content(
        testbrowser):
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    settings['author_articles_page_size'] = 4
    es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    es.results = [
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/01'},
        {'uniqueId': 'http://xml.zeit.de/zeit-online/article/02'}]
    browser = testbrowser('/autoren/j_random')
    # 3 favourite_content + 1 solr result
    assert len(browser.cssselect('.teaser-small')) == 4


def test_view_author_comments_should_have_comments_area(
        application, dummy_request):
    author = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/autoren/author3')
    dummy_request.registry.settings['author_comment_page_size'] = '6'
    dummy_request.GET['p'] = '1'
    view = zeit.web.site.view_author.Comments(author, dummy_request)
    assert type(view.tab_areas[0]) == (
        zeit.web.site.view_author.UserCommentsPagination)


def test_view_author_comments_should_handle_no_comments_gracefully(
        application, dummy_request):
    author = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/autoren/author3')
    view = zeit.web.site.view_author.Comments(author, dummy_request)
    community = zope.component.getUtility(zeit.web.core.interfaces.ICommunity)
    with mock.patch.object(community, 'get_user_comments') as get:
        get.return_value = None
        area = view.tab_areas[0]
        assert type(area) == (
            zeit.web.site.view_author.UserCommentsPagination)
        assert area.total_pages == 0
        assert area.page == 1


def test_author_comments_should_correctly_validate_pagination(
        application, dummy_request, monkeypatch):
    mock_comments = mock.MagicMock(return_value={'comments': []})
    monkeypatch.setattr(
        zeit.web.core.comments.Community, 'get_user_comments', mock_comments)

    dummy_request.GET.clear()
    context = mock.Mock()
    context.uniqueId = 'http://xml.zeit.de/author'
    view = zeit.web.site.view_author.Comments(context, dummy_request)
    assert view.tab_areas is not None
    assert mock_comments.call_args[1]['page'] == 1

    dummy_request.GET['p'] = 'nan'
    view = zeit.web.site.view_author.Comments(context, dummy_request)
    assert view.tab_areas is not None
    assert mock_comments.call_args[1]['page'] == 1

    dummy_request.GET['p'] = '3'
    view = zeit.web.site.view_author.Comments(context, dummy_request)
    assert view.tab_areas is not None
    assert mock_comments.call_args[1]['page'] == 3


def test_author_contact_should_be_fully_rendered(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'author_feedback': True}.get)
    browser = testbrowser('/autoren/j_random')
    container = browser.cssselect('.author-contact')[0]
    items = container.cssselect('.author-contact__item')
    twitter = container.cssselect('.author-contact__icon--twitter')
    facebook = container.cssselect('.author-contact__icon--facebook')
    instagram = container.cssselect('.author-contact__icon--instagram')

    assert len(items) == 4
    assert len(twitter) == 1
    assert len(facebook) == 1
    assert len(instagram) == 1


def test_author_feedback_should_be_fully_rendered(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'author_feedback': True}.get)
    browser = testbrowser('/autoren/j_random/feedback')
    container = browser.cssselect('.feedback-section')[0]
    form = container.cssselect('.feedback-form')
    title = container.cssselect('.feedback-form__inner p')[0].text
    textarea = container.cssselect('#feedbacktext')
    mail_input = container.cssselect('#feedbackmail')

    assert len(form) == 1
    assert title == 'Ihr Feedback an J. Random Hacker'
    assert len(textarea) == 1
    assert len(mail_input) == 1


def test_author_should_have_user_comments(testbrowser, clock):
    clock.freeze(datetime.datetime(2015, 12, 9))
    browser = testbrowser('/autoren/author3/kommentare')

    comments = browser.cssselect('.user-comment')

    # comment *without* title
    assert 'Ich habe den Halbsatz' in comments[0].cssselect(
        '.user-comment__text > p')[0].text
    # comment *with* title
    assert 'Hmmmmmm' == comments[1].cssselect(
        '.user-comment__text > p')[0].text

    assert '17. November 2015, verfasst zu:' == comments[0].cssselect(
        '.user-comment__date')[0].text

    assert '?cid=5572182#cid-5572182' in comments[0].cssselect(
        '.user-comment__article-link')[0].get('href')


def test_author_biography_should_be_fully_rendered(testbrowser):
    browser = testbrowser('/autoren/j_random')
    bio = browser.cssselect('.author-biography')
    assert 'Das ist die Biographie' in bio[0].text
    summary = browser.cssselect('.author-header__summary')
    assert 'Redakteur im Ressort Digital' in summary[0].text
    assert browser.cssselect('.author-questions')


def test_author_first_favorite_article_should_force_mobile_images(application):
    author = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/autoren/j_random')
    request = pyramid.testing.DummyRequest()
    view = zeit.web.site.view_author.Author(author, request)
    teasers = view.area_favourite_content.values()
    assert teasers[0].force_mobile_image
    assert not teasers[1].force_mobile_image


def test_author_handles_missing_profile_data_right(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/author/profile.html')
    author = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/autoren/j_random')
    author.topiclink_url_1 = None
    author.topiclink_url_2 = None
    author.topiclink_url_3 = None
    author.biography = ''
    author.email = ''
    author.twitter = ''
    author.facebook = ''
    author.instagram = ''
    author.bio_questions['hobby'] = None
    author.bio_questions['person'] = None
    request = pyramid.testing.DummyRequest()
    view = zeit.web.site.view_author.Author(author, request)
    html_str = tpl.render(view=view, context=view.context)
    select = lxml.html.fromstring(html_str).cssselect

    assert len(select('.author-topics')) == 0
    assert len(select('.author-biography')) == 0
    assert len(select('.author-contact')) == 0
    assert len(select('.author-questions__text')) == 5


def test_author_has_correct_open_graph_image(testbrowser):
    select = testbrowser('/autoren/julia_zange').cssselect
    url = ('http://localhost/zeit-online/cp-content/'
           'author_images/Julia_Zange/wide__1300x731')
    assert select('meta[property="og:image"]')[0].get('content') == url
    assert select('meta[property="og:image:width"]')[0].get('content') == (
        '1300')
    assert select('meta[property="og:image:height"]')[0].get('content') == (
        '731')
    assert select('meta[name="twitter:image"]')[0].get('content') == url
    assert select('link[rel="image_src"]')[0].get('href') == url


def test_author_page_has_correct_pagination_information(
        application, dummy_request):
    es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    es.results = ([{'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/01'}
                   for i in range(22)])

    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/autoren/j_random')
    dummy_request.path_info = u'/autoren/j_random'

    view = zeit.web.site.view_author.Author(content, dummy_request)
    assert view.canonical_url == 'http://example.com/autoren/j_random'
    assert view.next_page_url == 'http://example.com/autoren/j_random?p=2'
    assert view.prev_page_url is None
    assert view.meta_robots == 'index,follow,noarchive'
    assert view.pagination.get('current') == 1
    assert view.pagination.get('total') == 3
    assert view.webtrekk['customParameter']['cp3'] == '1/3'

    dummy_request.GET['p'] = '2'
    view = zeit.web.site.view_author.Author(content, dummy_request)
    assert view.canonical_url == 'http://example.com/autoren/j_random?p=2'
    assert view.next_page_url == 'http://example.com/autoren/j_random?p=3'
    assert view.prev_page_url == 'http://example.com/autoren/j_random'
    assert view.meta_robots == 'noindex,follow,noarchive'
    assert view.pagination.get('current') == 2
    assert view.pagination.get('total') == 3
    assert view.webtrekk['customParameter']['cp3'] == '2/3'

    dummy_request.GET['p'] = '3'
    view = zeit.web.site.view_author.Author(content, dummy_request)
    assert view.canonical_url == 'http://example.com/autoren/j_random?p=3'
    assert view.next_page_url is None
    assert view.prev_page_url == 'http://example.com/autoren/j_random?p=2'
    assert view.meta_robots == 'noindex,follow,noarchive'
    assert view.pagination.get('current') == 3
    assert view.pagination.get('total') == 3
    assert view.webtrekk['customParameter']['cp3'] == '3/3'


def test_author_page_contains_pagination_information(testbrowser):
    es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    es.results = ([{'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/01'}
                   for i in range(22)])

    url = 'http://localhost/autoren/j_random'

    select = testbrowser('/autoren/j_random').cssselect
    assert select('link[rel="canonical"]')[0].get('href') == url
    assert select('link[rel="next"]')[0].get('href') == url + '?p=2'
    assert not select('link[rel="prev"]')
    assert select('meta[name="robots"]')[0].get('content') == (
        'index,follow,noarchive')

    select = testbrowser('/autoren/j_random?p=3').cssselect
    assert select('link[rel="canonical"]')[0].get('href') == url + '?p=3'
    assert not select('link[rel="next"]')
    assert select('link[rel="prev"]')[0].get('href') == url + '?p=2'
    assert select('meta[name="robots"]')[0].get('content') == (
        'noindex,follow,noarchive')


def test_author_comments_page_contains_pagination_information(testbrowser):
    url = 'http://localhost/autoren/author3/kommentare'

    select = testbrowser('/autoren/author3/kommentare').cssselect
    assert select('link[rel="canonical"]')[0].get('href') == url
    assert select('link[rel="next"]')[0].get('href') == url + '?p=2'
    assert not select('link[rel="prev"]')
    assert select('meta[name="robots"]')[0].get('content') == (
        'index,follow,noarchive')

    select = testbrowser('/autoren/author3/kommentare?p=2').cssselect
    assert select('link[rel="canonical"]')[0].get('href') == url + '?p=2'
    assert select('link[rel="next"]')[0].get('href') == url + '?p=3'
    assert select('link[rel="prev"]')[0].get('href') == url
    assert select('meta[name="robots"]')[0].get('content') == (
        'noindex,follow,noarchive')

    select = testbrowser('/autoren/author3/kommentare?p=3').cssselect
    assert select('link[rel="canonical"]')[0].get('href') == url + '?p=3'
    assert not select('link[rel="next"]')
    assert select('link[rel="prev"]')[0].get('href') == url + '?p=2'
    assert select('meta[name="robots"]')[0].get('content') == (
        'noindex,follow,noarchive')


def test_authorpage_has_follow_push_button(selenium_driver, testserver):
    zeit.web.core.application.FEATURE_TOGGLES.set('push_for_author_in_app')
    driver = selenium_driver
    select = driver.find_elements_by_css_selector
    driver.get('%s/autoren/j_random?app-content' % testserver.url)
    expected_link = 'zeitapp://subscribe/{segment}/{id}'.format(
        segment='authors', id='c5520263-4393-43d3-b6a9-3d390e12ad11')
    assert len(
        select('a[href^="{}"]'.format(expected_link))) == 1
