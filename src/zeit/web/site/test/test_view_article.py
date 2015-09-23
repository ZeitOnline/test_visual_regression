# -*- coding: utf-8 -*-
import base64
import datetime
import lxml.etree
import mock
import pytest
import pyramid.testing

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  # NOQA
from selenium.webdriver.support.ui import WebDriverWait

from zeit.cms.checkout.helper import checked_out
import zeit.web.site.view_article
import zeit.cms.interfaces


screen_sizes = ((320, 480, True), (520, 960, True),
                (768, 1024, False), (980, 1024, False))


@pytest.fixture(scope='session', params=screen_sizes)
def screen_size(request):
    return request.param


def test_article_should_render_full_view(testbrowser):
    browser = testbrowser('/zeit-online/article/zeit/komplettansicht')
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/zeit')
    assert len(browser.cssselect(
        '.article-page > p.paragraph')) == article.paragraphs


def test_article_single_page_has_no_pagination(testbrowser):
    select = testbrowser('/zeit-online/article/simple').cssselect

    assert len(select('.summary, .byline, .metadata')) == 3
    assert len(select('.article-pagination')) == 0
    assert len(select('.article-toc')) == 0


def test_article_full_view_has_no_pagination(testbrowser):
    select = testbrowser('/zeit-online/article/zeit/komplettansicht').cssselect

    assert len(select('.summary, .byline, .metadata')) == 3
    assert len(select('.article-pagination')) == 0
    assert len(select('.article-toc')) == 0


def test_article_pagination(testbrowser):
    select = testbrowser('/zeit-online/article/zeit').cssselect
    nexttitle = select('.article-pagination__nexttitle')
    numbers = select('.article-pager__number')

    assert len(select('.summary, .byline, .metadata')) == 3
    assert len(select('.article__page-teaser')) == 0
    assert len(select('.article-pagination')) == 1
    assert len(nexttitle) == 1
    assert nexttitle[0].text.strip() == (
        u'Der Horror von Crystal wurzelt in der Normalität')
    assert len(numbers) == 5
    assert '--current' in numbers[0].get('class')
    assert len(select('.article-toc')) == 1
    assert len(select('.article-toc__item')) == 5
    assert '--current' in select('.article-toc__item')[0].get('class')


def test_article_pagination_active_state(testbrowser):
    select = testbrowser('/zeit-online/article/zeit/seite-3').cssselect

    assert len(select('.summary, .byline, .metadata')) == 0
    assert select('.article__page-teaser')[0].text.strip() == (
        u'Seite 3/5:')
    assert select('.article__page-teaser > h1')[0].text.strip() == (
        u'Man wird schlank und lüstern')
    assert select('.article-pagination__nexttitle')[0].text.strip() == (
        u'Aus dem abenteuerlustigen Mädchen vom Dorf wurde ein Junkie')
    assert '--current' in select('.article-pager__number')[2].get('class')
    assert len(select('.article-toc')) == 1
    assert len(select('.article-toc__item')) == 5
    assert '--current' in select('.article-toc__item')[2].get('class')


def test_article_page_1_has_correct_h1(testbrowser):
    select = testbrowser('/zeit-online/article/zeit').cssselect
    node = '.article__item > h1 > .article-heading__title'
    assert select(node)[0].text.strip() == (
        u'Nancy braucht was Schnelles'), (
        'article headline is not h1')


def test_article_page_2_has_correct_h1(testbrowser):
    select = testbrowser('/zeit-online/article/zeit/seite-2').cssselect
    node = '.article__page-teaser > h1'
    assert select(node)[0].text.strip() == (
        u'Der Horror von Crystal wurzelt in der Normalität'), (
        'article page teaser is not h1')


def test_article_page_teaserless_has_correct_h1(testbrowser):
    select = testbrowser('/zeit-online/article/zeit/seite-5').cssselect
    node = '.article__item > h1 > .article-heading__title'
    assert select(node)[0].text.strip() == (
        u'Nancy braucht was Schnelles'), (
        'article headline is not h1')


def test_article_complete_has_correct_h1(testbrowser):
    select = testbrowser('/zeit-online/article/zeit/komplettansicht').cssselect
    node = '.article__item > h1 > .article-heading__title'
    assert select(node)[0].text.strip() == (
        u'Nancy braucht was Schnelles'), (
        'article headline is not h1')


def test_article_plain_has_correct_h1(testbrowser):
    select = testbrowser('/zeit-online/article/simple').cssselect
    node = '.article__item > h1 > .article-heading__title'
    assert select(node)[0].text.strip() == (
        u'Williams wackelt weiter, steht aber im Viertelfinale'), (
        'article headline must be h1')


def test_article_page_1_has_correct_title(testbrowser):
    select = testbrowser('/zeit-online/article/zeit').cssselect
    assert select('title')[0].text.strip() == (
        u'Crystal Meth: Nancy braucht was Schnelles |\xa0ZEIT ONLINE'), (
        'article headline is not title')


def test_article_page_2_has_correct_title(testbrowser):
    select = testbrowser('/zeit-online/article/zeit/seite-2').cssselect
    assert select('title')[0].text.strip() == (
        u'Crystal Meth: Der Horror von Crystal '
        u'wurzelt in der Normalität |\xa0ZEIT ONLINE'), (
        'article page teaser is not title')


def test_article_page_teaserless_has_correct_title(testbrowser):
    select = testbrowser('/zeit-online/article/zeit/seite-5').cssselect
    assert select('title')[0].text.strip() == (
        u'Crystal Meth: Nancy braucht was Schnelles |\xa0ZEIT ONLINE'), (
        'article headline is not title')


def test_article_complete_has_correct_title(testbrowser):
    select = testbrowser('/zeit-online/article/zeit/komplettansicht').cssselect
    assert select('title')[0].text.strip() == (
        u'Crystal Meth: Nancy braucht was Schnelles |\xa0ZEIT ONLINE'), (
        'article headline is not title')


def test_article_plain_has_correct_title(testbrowser):
    select = testbrowser('zeit-online/article/02').cssselect
    assert select('title')[0].text.strip() == (
        u'Zwei Baguettes und ein Zimmer bitte |\xa0ZEIT ONLINE'), (
        'article headline is not title')


def test_fresh_breaking_news_article_renders_breaking_bar(testbrowser):
    browser = testbrowser('/zeit-online/article/eilmeldungsartikel')

    assert len(browser.cssselect('.breaking-news-banner')) == 1
    assert len(browser.cssselect('.breaking-news-heading')) == 1


def test_stale_breaking_news_article_must_not_render_breaking_bar(testbrowser):
    browser = testbrowser('/zeit-online/article/alte-eilmeldung')

    assert len(browser.cssselect('.breaking-news-banner')) == 0
    assert len(browser.cssselect('.breaking-news-heading')) == 0


def test_schema_org_main_content_of_page(testbrowser):
    select = testbrowser('/zeit-online/article/01').cssselect

    assert len(select('main[itemprop="mainContentOfPage"]')) == 1


def test_schema_org_article_mark_up(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    selector = 'article[itemtype="http://schema.org/Article"][itemscope]'
    article = browser.cssselect(selector)
    assert len(article) == 1
    select = article[0].cssselect

    # articleBody
    assert len(select('div[itemprop="articleBody"]')) == 1

    # headline
    headline = select('h1[itemprop="headline"]')
    assert len(headline) == 1
    assert headline[0].text_content().strip() == (
        u'"Der Hobbit": Geht\'s noch gr\xf6\xdfer?')

    # description
    assert len(select('div[itemprop="description"]')) == 1

    # author
    selector = (
        '*[itemtype="http://schema.org/Person"][itemprop="author"][itemscope]')
    author = select(selector)
    assert len(author) == 1
    assert len(author[0].cssselect('a[itemprop="url"]')) == 1
    name = author[0].cssselect('span[itemprop="name"]')
    assert len(name) == 1
    assert name[0].text == 'Wenke Husmann'

    # image
    assert len(select('img[itemprop="image"]')) == 1

    # datePublished
    assert len(select('time[itemprop="datePublished"]')) == 1


def test_multipage_article_should_designate_meta_pagination(testbrowser):
    browser = testbrowser('/zeit-online/article/zeit')
    assert not browser.xpath('//head/link[@rel="prev"]')
    href = browser.xpath('//head/link[@rel="next"]')[0].attrib.get('href')
    assert href.endswith('zeit-online/article/zeit/seite-2')

    browser = testbrowser('/zeit-online/article/zeit/seite-2')
    href = browser.xpath('//head/link[@rel="prev"]')[0].attrib.get('href')
    assert href.endswith('zeit-online/article/zeit')
    href = browser.xpath('//head/link[@rel="next"]')[0].attrib.get('href')
    assert href.endswith('zeit-online/article/zeit/seite-3')

    browser = testbrowser('/zeit-online/article/zeit/seite-5')
    href = browser.xpath('//head/link[@rel="prev"]')[0].attrib.get('href')
    assert href.endswith('zeit-online/article/zeit/seite-4')
    assert not browser.xpath('//head/link[@rel="next"]')


def test_other_page_types_should_not_designate_meta_pagination(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    assert not browser.xpath('//head/link[@rel="prev"]')
    assert not browser.xpath('//head/link[@rel="next"]')

    browser = testbrowser('/zeit-online/index')
    assert not browser.xpath('//head/link[@rel="prev"]')
    assert not browser.xpath('//head/link[@rel="next"]')


def test_article_meta_should_show_comment_count(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    count = browser.cssselect('.metadata__commentcount')[0].text
    assert count == '42 Kommentare'


def test_article_meta_should_omit_comment_count_if_no_comments_present(
        testbrowser):
    browser = testbrowser('/zeit-online/article/simple')
    assert len(browser.cssselect('.metadata__commentcount')) == 0


def test_article_obfuscated_source_without_date_print_published():
    content = mock.Mock()
    content.product.label = content.product.title = 'DIE ZEIT'
    content.product.show = 'issue'
    content.copyrights = ''
    content.volume = 1
    content.year = 2011
    view = zeit.web.site.view_article.Article(content, mock.Mock())
    view.date_print_published = None
    source = u'DIE ZEIT Nr.\u00A01/2011'
    assert view.obfuscated_source == base64.b64encode(source.encode('latin-1'))


def test_article_sharing_menu_should_open_and_close(
        testserver, selenium_driver):
    selenium_driver.set_window_size(320, 480)
    selenium_driver.get('{}/zeit-online/article/01'.format(testserver.url))

    sharing_menu_selector = '.sharing-menu > .sharing-menu__items'
    sharing_menu_target = selenium_driver.find_element_by_css_selector(
        '.sharing-menu > .sharing-menu__title.js-sharing-menu')
    sharing_menu_items = selenium_driver.find_element_by_css_selector(
        sharing_menu_selector)

    assert sharing_menu_items.is_displayed() is False, (
        'sharing menu should be hidden by default')

    sharing_menu_target.click()
    assert sharing_menu_items.is_displayed(), (
        'sharing menu should be visible after interaction')

    sharing_menu_target.click()
    # we need to wait for the CSS animation to finish
    # so the sharing menu is actually hidden
    condition = EC.invisibility_of_element_located((
        By.CSS_SELECTOR, sharing_menu_selector))
    assert WebDriverWait(
        selenium_driver, 1).until(condition), (
        'sharing menu should hide again on click')


def test_article_sharing_menu_should_hide_whatsapp_link_tablet_upwards(
        testserver, selenium_driver):
    selenium_driver.set_window_size(768, 800)
    selenium_driver.get('{}/zeit-online/article/01'.format(testserver.url))

    sharing_menu_target = selenium_driver.find_element_by_css_selector(
        '.sharing-menu > .sharing-menu__title.js-sharing-menu')
    whatsapp_item = selenium_driver.find_element_by_css_selector(
        '.sharing-menu__item--whatsapp')

    sharing_menu_target.click()
    assert not(whatsapp_item.is_displayed()), (
        'Sharing link to WhatsApp should be hidden on tablet & desktop')


def test_article_sharing_links_should_be_url_encoded(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    # it's hard to check for url-encodedness,
    # but checking for unencoded spaces nearly should do the trick
    spacey_sharing_links = browser.cssselect(
        '.sharing-menu .sharing-menu__link[href*=" "]')
    assert len(spacey_sharing_links) == 0


def test_article_tags_are_present_and_limited(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    tags = browser.cssselect('.article-tags')

    assert len(tags) == 1
    assert len(tags[0].find_class('article-tags__title')) == 1
    assert len(tags[0].find_class('article-tags__link')) == 6


def test_infobox_in_article_is_shown(testbrowser):
    select = testbrowser('/zeit-online/article/infoboxartikel').cssselect
    assert len(select('aside#sauriersindsuper.infobox')) == 1
    assert len(select('#sauriersindsuper .infobox-tab__title')) == 6


def test_infobox_mobile_actions(testserver, selenium_driver, screen_size):
    selenium_driver.set_window_size(screen_size[0], screen_size[1])
    selenium_driver.get('{}/zeit-online/article/infoboxartikel'.format(
        testserver.url))
    infobox = selenium_driver.find_element_by_id('sauriersindsuper')
    tabnavigation = infobox.find_elements_by_class_name('infobox__navigation')
    tabpanels = infobox.find_elements_by_class_name('infobox-tab__content')
    clicker = infobox.find_elements_by_css_selector(
        '.infobox-tab .infobox-tab__title')

    assert infobox.is_displayed(), 'Infobox missing'

    if screen_size[0] == 320 or screen_size[0] == 520:
        assert not tabnavigation[0].is_displayed(), 'Mobile not accordion'
        assert tabpanels[0].get_attribute('aria-hidden') == 'true'
        assert tabpanels[1].get_attribute('aria-hidden') == 'true'
        assert tabpanels[2].get_attribute('aria-hidden') == 'true'
        assert tabpanels[3].get_attribute('aria-hidden') == 'true'
        assert tabpanels[4].get_attribute('aria-hidden') == 'true'
        assert tabpanels[5].get_attribute('aria-hidden') == 'true'
        clicker[0].click()
        assert tabpanels[0].get_attribute('aria-hidden') == 'false'
        clicker[1].click()
        assert tabpanels[1].get_attribute('aria-hidden') == 'false'
        clicker[3].click()
        assert tabpanels[3].get_attribute('aria-hidden') == 'false'
        clicker[5].click()
        assert tabpanels[5].get_attribute('aria-hidden') == 'false'
        clicker[0].click()
        assert tabpanels[0].get_attribute('aria-hidden') == 'true'


def test_infobox_desktop_actions(testserver, selenium_driver, screen_size):
    selenium_driver.set_window_size(screen_size[0], screen_size[1])
    selenium_driver.get('{}/zeit-online/article/infoboxartikel'.format(
        testserver.url))
    infobox = selenium_driver.find_element_by_id('sauriersindsuper')
    tabnavigation = infobox.find_elements_by_class_name(
        'infobox__navigation')[0]
    tabpanels = infobox.find_elements_by_class_name('infobox-tab__content')
    clicker = infobox.find_elements_by_css_selector(
        '.infobox__navigation .infobox-tab__title')

    assert infobox.is_displayed(), 'Infobox missing'

    if screen_size[0] > 767:
        assert tabnavigation.is_displayed(), 'Desktop not Tabs'
        assert tabpanels[0].get_attribute('aria-hidden') == 'false'
        assert tabpanels[1].get_attribute('aria-hidden') == 'true'
        assert tabpanels[2].get_attribute('aria-hidden') == 'true'
        assert tabpanels[3].get_attribute('aria-hidden') == 'true'
        assert tabpanels[4].get_attribute('aria-hidden') == 'true'
        assert tabpanels[5].get_attribute('aria-hidden') == 'true'
        clicker[0].click()
        assert tabpanels[0].get_attribute('aria-hidden') == 'false'
        clicker[1].click()
        assert tabpanels[0].get_attribute('aria-hidden') == 'true'
        assert tabpanels[1].get_attribute('aria-hidden') == 'false'
        clicker[3].click()
        assert tabpanels[0].get_attribute('aria-hidden') == 'true'
        assert tabpanels[1].get_attribute('aria-hidden') == 'true'
        assert tabpanels[2].get_attribute('aria-hidden') == 'true'
        assert tabpanels[3].get_attribute('aria-hidden') == 'false'


def test_article_has_news_source_as_list():
    content = mock.Mock()
    content.copyrights = 'ZEIT ONLINE, Reuters'

    view = zeit.web.site.view_article.Article(content, mock.Mock())
    assert view.news_source == 'ZEITONLINE;Reuters'


def test_article_has_news_source_dpa():
    content = mock.Mock()
    content.ressort = 'News'
    content.product.id = 'News'
    view = zeit.web.site.view_article.Article(content, mock.Mock())
    assert view.news_source == "dpa"


def test_article_has_news_source_sid():
    content = mock.Mock()
    content.product.id = 'SID'
    view = zeit.web.site.view_article.Article(content, mock.Mock())
    assert view.news_source == "Sport-Informations-Dienst"


def test_article_has_news_source_empty():
    content = mock.Mock()
    content.copyrights = None

    view = zeit.web.site.view_article.Article(content, mock.Mock())
    assert view.news_source == ''


def test_article_news_source_should_not_break_without_product():
    # While product is required in vivi, we've seen content without one
    # in production preview (presumably while the article is being created).
    content = mock.Mock()
    content.copyrights = None
    content.ressort = 'News'
    content.product = None

    view = zeit.web.site.view_article.Article(content, mock.Mock())
    assert view.news_source == ''


def test_adcontroller_values_return_values_on_article(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/infoboxartikel')
    adcv = [
        ('$handle', 'artikel'),
        ('level2', u'wissen'),
        ('level3', 'umwelt'),
        ('level4', ''),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline'),
        ('tma', '')]
    view = view = zeit.web.site.view_article.Article(content, mock.Mock())
    assert adcv == view.adcontroller_values


def test_article_view_renders_alldevices_raw_box(testbrowser):
    browser = testbrowser('/zeit-online/article/raw-box')
    assert 'fVwQok9xnLGOA' in browser.contents


def test_article_skips_raw_box_not_suitable_for_alldevices(testbrowser):
    browser = testbrowser('/zeit-online/article/raw-box')
    assert 'cYhaIIyjjxg1W' not in browser.contents


def test_nextread_is_placed_on_article(testbrowser):
    browser = testbrowser('/zeit-online/article/simple-nextread')
    assert len(browser.cssselect('#nextread')) == 1


def test_nextread_date_looks_less_like_a_date_for_google(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/article/nextread.tpl')
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/simple-nextread')
    request = mock.MagicMock()
    request.route_url.return_value = 'http://foo.bar/'
    view = zeit.web.site.view_article.Article(content, request)
    html_str = tpl.render(view=view, request=request)
    html = lxml.html.fromstring(html_str)
    datetime = html.cssselect('.nextread__dt')
    assert datetime[0].tag == 'span'
    assert not any(x in datetime[0].get('class') for x in ['date', 'time'])


def test_nextread_is_responsive(testserver, selenium_driver, screen_size):
    url = '{}/zeit-online/article/simple-nextread'.format(testserver.url)
    selenium_driver.set_window_size(screen_size[0], screen_size[1])
    selenium_driver.get(url)
    nextread = selenium_driver.find_element_by_id('nextread')

    assert nextread.is_displayed(), 'Nextread missing'

    if screen_size[0] == 320:
        assert nextread.size.get('height') > 137

    if screen_size[0] == 520:
        assert nextread.size.get('height') > 220

    if screen_size[0] == 768:
        assert nextread.size.get('height') < 350

    if screen_size[0] == 980:
        assert nextread.size.get('height') < 450


def test_publisher_nextread_on_article_has_own_template(testbrowser):
    browser = testbrowser('/zeit-online/article/simple-verlagsnextread')
    assert len(browser.cssselect('.nextread-advertisement')) == 1


def test_zon_nextread_teaser_block_has_teasers_available(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/simple-nextread')
    nextread = zeit.web.core.interfaces.INextread(context)
    assert hasattr(nextread, '__iter__')
    assert len(nextread) == 1
    assert nextread[0].uniqueId.endswith('/zeit-online/article/zeit')


def test_article_column_should_have_no_body_image(testbrowser):
    browser = testbrowser('/zeit-online/cp-content/kolumne')
    assert not browser.cssselect('.article-body img')


def test_article_column_author_image_should_be_present(testbrowser):
    browser = testbrowser('/zeit-online/cp-content/kolumne')
    img = browser.cssselect(
        '.column-heading__author .column-heading__media-item')
    ratio = img[0].get('data-ratio')
    src = img[0].get('src')
    assert src != "" and ratio != ""


def test_article_should_not_break_on_author_without_image(
        testbrowser, workingcopy):
    author = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/autoren/author3')
    with checked_out(author) as co:
        co.image_group = None
    browser = testbrowser('/zeit-online/cp-content/kolumne')
    assert not browser.cssselect(
        '.column-heading__author .column-heading__media-item')


def test_article_should_not_break_without_author(
        testbrowser, workingcopy):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/kolumne')
    with checked_out(content) as co:
        co.authorships = ()
    browser = testbrowser('/zeit-online/cp-content/kolumne')
    assert not browser.cssselect(
        '.column-heading__author .column-heading__media-item')


def test_article_for_column_without_authorimage_should_be_rendered_default(
        testbrowser):
    browser = testbrowser('/zeit-online/cp-content/kolumne-ohne-autorenbild')

    assert len(browser.cssselect('.article--columnarticle')) == 0
    assert len(browser.cssselect('.column-heading')) == 0


def test_article_column_should_be_identifiable_by_suitable_css_class(
        testbrowser):
    browser = testbrowser('/zeit-online/cp-content/kolumne')
    assert browser.cssselect('.article.article--columnarticle')
    assert browser.cssselect('.article-body.article-body--columnarticle')


def test_article_column_pages_should_render_correctly(testbrowser):
    browser = testbrowser('/zeit-online/article/fischer/seite-2')
    assert browser.cssselect('.column-heading__upper')
    assert len(browser.cssselect('.column-heading__lower')) == 0
    assert browser.cssselect('.article__page-teaser--column')


def test_article_should_show_main_image_from_imagegroup(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    images = browser.cssselect('.article-body img')
    assert 'filmstill-hobbit-schlacht-fuenf-hee' in images[0].get('src')


def test_article_should_have_proper_meetrics_integration(
        testserver, testbrowser):
    browser = testbrowser(
        '{}/zeit-online/article/01'.format(testserver.url))
    meetrics = browser.cssselect(
        'script[src="http://s62.mxcdn.net/bb-serve/mtrcs_225560.js"]')
    assert len(meetrics) == 1


def test_breaking_news_article_shows_date_first_released(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/article_breaking.html')
    view = mock.Mock()
    view.date_first_released = datetime.time(11, 55, 0)
    lines = tpl.blocks['breaking_news'](tpl.new_context({'view': view}))
    html_str = ' '.join(lines).strip()
    html = lxml.html.fromstring(html_str)
    time = html.cssselect('.breaking-news-banner__time')
    assert time[0].text == '11:55 Uhr'


def test_breaking_news_banner_shows_date_first_released(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/breaking_news.tpl')
    view = mock.Mock()
    view.breaking_news.published = True
    view.breaking_news.date_first_released = datetime.time(11, 55, 0)
    html_str = tpl.render(view=view)
    html = lxml.html.fromstring(html_str)
    time = html.cssselect('.breaking-news-banner__time')
    assert time[0].text == '11:55 Uhr'


def test_tile7_is_rendered_on_articles_with_multiple_pages(testbrowser):
    selector = ('#ad-desktop-7', '#ad-mobile-4')

    browser = testbrowser('/zeit-online/article/zeit')
    assert len(browser.cssselect(selector[0])) == 1
    assert len(browser.cssselect(selector[1])) == 1

    browser = testbrowser('/zeit-online/article/zeit/seite-2')
    assert len(browser.cssselect(selector[0])) == 1
    assert len(browser.cssselect(selector[1])) == 1

    browser = testbrowser('/zeit-online/article/zeit/seite-5')
    assert len(browser.cssselect(selector[0])) == 1
    assert len(browser.cssselect(selector[1])) == 1


def test_tiles7_9_are_rendered_on_articles_with_multiple_pages_on_onepage_view(
        testbrowser):
    browser = testbrowser('/zeit-online/article/zeit/komplettansicht')
    assert len(browser.cssselect('#ad-desktop-7')) == 1
    assert len(browser.cssselect('#ad-mobile-4')) == 1
    assert len(browser.cssselect('#ad-desktop-9')) == 1


def test_article_ads_should_have_pagetype_modifier(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    assert len(browser.cssselect('#ad-desktop-7')) == 1
    assert 'ad-desktop--7-on-article' in browser.contents


def test_does_not_break_when_author_has_no_display_name(
        testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/08')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    with mock.patch('zeit.content.author.author.Author.display_name', None):
        assert article_view.authors_list == ''


def test_article_views_have_page_numbers_in_data_attribute(testbrowser):
    select_fullview = testbrowser(
        '/zeit-online/article/zeit/komplettansicht').cssselect
    assert len(select_fullview('.article-page[data-page-number="1"]')) == 1
    assert len(select_fullview('.article-page[data-page-number="2"]')) == 1
    assert len(select_fullview('.article-page[data-page-number="3"]')) == 1
    assert len(select_fullview('.article-page[data-page-number="4"]')) == 1
    assert len(select_fullview('.article-page[data-page-number="5"]')) == 1

    select_firstpage = testbrowser(
        '/zeit-online/article/zeit').cssselect
    assert len(select_firstpage('.article-page[data-page-number="1"]')) == 1
    assert len(select_firstpage('.article-page[data-page-number="2"]')) == 0

    select_page3 = testbrowser(
        '/zeit-online/article/zeit/seite-3').cssselect
    assert len(select_page3('.article-page[data-page-number="1"]')) == 0
    assert len(select_page3('.article-page[data-page-number="3"]')) == 1


def test_messy_archive_metadata_should_have_minimal_breadcrumbs(
        application, monkeypatch):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', u'ZEI')
    monkeypatch.setattr(
        zeit.content.article.article.Article, u'year', None)
    monkeypatch.setattr(
        zeit.content.article.article.Article, u'volume', u'xx')
    article_view = zeit.web.site.view_article.Article(context, mock.Mock())
    # Fallback to default breadcrumbs, including the article title
    assert article_view.title in article_view.breadcrumbs[1][0]


def test_old_archive_text_without_divisions_should_render_paragraphs(
        testbrowser):
    browser = testbrowser('/zeit-online/article/alter-archivtext')
    assert len(browser.cssselect('.article__item.paragraph')) == 7
    assert len(browser.cssselect('.article-pager__number')) == 3


def test_imported_article_has_special_meta_robots(
        application, monkeypatch):

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    request = pyramid.testing.DummyRequest()

    # test ZEAR
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', u'ZEAR')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'ressort', u'Fehler')
    article_view = zeit.web.site.view_article.Article(context, request)
    assert article_view.meta_robots == 'noindex,follow', (
        'wrong robots for ZEAR')

    # test TGS
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', u'TGS')
    article_view = zeit.web.site.view_article.Article(context, request)
    assert article_view.meta_robots == 'noindex,follow', (
        'wrong robots for TGS')

    # test HaBl
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', u'HaBl')
    article_view = zeit.web.site.view_article.Article(context, request)
    assert article_view.meta_robots == 'noindex,follow', (
        'wrong robots for HaBl')

    # test WIWO
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', u'WIWO')
    article_view = zeit.web.site.view_article.Article(context, request)
    assert article_view.meta_robots == 'noindex,follow', (
        'wrong robots for WIWO')

    # test GOLEM
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', u'GOLEM')
    article_view = zeit.web.site.view_article.Article(context, request)
    assert article_view.meta_robots == 'noindex,follow', (
        'wrong robots for GOLEM')

    # test ZEI
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', u'ZEI')
    article_view = zeit.web.site.view_article.Article(context, request)
    assert article_view.meta_robots == 'index,follow,noodp,noydir,noarchive', (
        'wrong robots for ZEI')

    # test no product id
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', None)
    article_view = zeit.web.site.view_article.Article(context, request)
    assert article_view.meta_robots == 'index,follow,noodp,noydir,noarchive', (
        'wrong robots for none product article')


def test_robots_rules_for_angebote_articles(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    request = pyramid.testing.DummyRequest()

    # usual angebot
    request.path = '/angebote/buchtipp/ishiguro/index'
    view = zeit.web.site.view_article.Article(article, request)
    assert view.meta_robots == 'index,nofollow,noodp,noydir,noarchive', (
        'wrong robots for usual angebot')

    # partnersuche
    request.path = '/angebote/partnersuche/test'
    view = zeit.web.site.view_article.Article(article, request)
    assert view.meta_robots == 'index,follow,noodp,noydir,noarchive', (
        'wrong robots for partnersuche')


def test_robots_rules_for_diverse_articles(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    request = mock.Mock()
    request.url = 'http://localhost'

    # test folder
    request.path = '/test/article'
    view = zeit.web.site.view_article.Article(article, request)
    assert view.meta_robots == 'noindex,follow,noodp,noydir,noarchive', (
        'wrong robots for test folder')

    # templates folder
    request.path = '/templates/article'
    view = zeit.web.site.view_article.Article(article, request)
    assert view.meta_robots == 'noindex,follow,noodp,noydir,noarchive', (
        'wrong robots for templates folder')

    # banner folder
    request.path = '/banner/article'
    view = zeit.web.site.view_article.Article(article, request)
    assert view.meta_robots == 'noindex,follow,noodp,noydir,noarchive', (
        'wrong robots for banner folder')

    # any folder
    request.path = '/any/article'
    view = zeit.web.site.view_article.Article(article, request)
    assert view.meta_robots == 'index,follow,noodp,noydir,noarchive', (
        'wrong robots for any other folder')


def test_article_doesnt_show_modified_date(testbrowser):
    select = testbrowser('/zeit-online/article/01').cssselect
    date_string = select('.metadata__date')[0].text
    assert date_string == '27. Mai 2015, 19:11 Uhr'


def test_video_in_article_is_there(testbrowser):
    article = testbrowser('/zeit-online/article/zeit')
    assert len(article.cssselect('.video-player__iframe')) == 1


def test_advertorial_marker_is_returned_correctly():
    content = mock.Mock()
    content.advertisement_title = 'YYY'
    content.advertisement_text = 'XXX'
    content.cap_title = 'ZZZ'
    view = zeit.web.site.view_article.Article(content, mock.Mock())
    assert view.advertorial_marker == ('YYY', 'XXX', 'Zzz')


def test_advertorial_marker_is_present(testbrowser):
    browser = testbrowser('zeit-online/article/angebot')
    assert len(browser.cssselect('.advertorial-marker')) == 1
    assert len(browser.cssselect('.advertorial-marker__title')) == 1
    assert len(browser.cssselect('.advertorial-marker__text')) == 1
    assert len(browser.cssselect('.advertorial-marker__label')) == 1


def test_canonical_url_should_omit_queries_and_hashes(testbrowser):
    browser = testbrowser('/zeit-online/article/zeit/seite-3?cid=123#comments')
    canonical_url = browser.cssselect('link[rel=canonical]')[0].attrib['href']
    assert canonical_url.endswith('zeit-online/article/zeit/seite-3')


def test_zeit_article_has_correct_meta_line(
        testserver, selenium_driver):

    selenium_driver.get('{}/zeit-online/article/zeit'.format(testserver.url))

    date = selenium_driver.find_element_by_css_selector(
        '.metadata__date')
    source = selenium_driver.find_element_by_css_selector(
        '.metadata__source')

    assert date.text == (u'12. Februar 2015, 4:32 Uhr /'
                         ' Editiert am 15. Februar 2015, 18:18 Uhr')
    assert source.text == (u'DIE ZEIT Nr. 5/2015, 29. Januar 2015')


def test_tgs_article_has_correct_meta_line(
        testserver, selenium_driver):

    selenium_driver.get(
        '{}/zeit-online/article/tagesspiegel'.format(testserver.url))

    date = selenium_driver.find_element_by_css_selector(
        '.metadata__date')
    source = selenium_driver.find_element_by_css_selector(
        '.metadata__source')

    assert date.text == (u'15. Februar 2015, 0:00 Uhr /'
                         ' Aktualisiert am 16. Februar 2015, 11:59 Uhr')
    assert source.text == (u'Erschienen im Tagesspiegel')


def test_zon_article_has_correct_meta_line(
        testserver, selenium_driver):

    selenium_driver.get(
        '{}/zeit-online/article/simple'.format(testserver.url))

    date = selenium_driver.find_element_by_css_selector(
        '.metadata__date')

    assert date.text == (u'1. Juni 2015, 17:12 Uhr /'
                         ' Aktualisiert am 1. Juni 2015, 17:12 Uhr')


def test_freeform_article_has_correct_meta_line(
        testserver, selenium_driver):

    selenium_driver.get(
        '{}/zeit-online/article/copyrights'.format(testserver.url))

    date = selenium_driver.find_element_by_css_selector(
        '.metadata__date')
    source = selenium_driver.find_element_by_css_selector(
        '.metadata__source')

    assert date.text == (u'15. Februar 2015, 0:00 Uhr /'
                         ' Aktualisiert am 16. Februar 2015, 11:59 Uhr')
    assert source.text == (u'Quelle: ZEIT ONLINE, dpa, Reuters, rav')


def test_afp_article_has_correct_meta_line(
        testserver, selenium_driver):

    selenium_driver.get(
        '{}/zeit-online/article/afp'.format(testserver.url))

    date = selenium_driver.find_element_by_css_selector(
        '.metadata__date')
    source = selenium_driver.find_element_by_css_selector(
        '.metadata__source')

    assert date.text == (u'15. Februar 2015, 0:00 Uhr /'
                         ' Aktualisiert am 16. Februar 2015, 11:59 Uhr')
    assert source.text == (u'Quelle: afp')


def test_article_should_have_large_facebook_and_twitter_images(testbrowser):
    doc = testbrowser('/zeit-online/article/01').document
    assert doc.xpath('//meta[@property="og:image"]/@content')[0].endswith(
        'zeit-online/image/filmstill-hobbit-schlacht-fuenf-hee/wide__1300x731')
    assert doc.xpath('//meta[@name="twitter:image"]/@content')[0].endswith(
        'zeit-online/image/filmstill-hobbit-schlacht-fuenf-hee/wide__1300x731')


def test_article_should_evaluate_display_mode_of_image_layout(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    main_image = browser.cssselect('.article-body img')[0]
    figure = main_image.xpath('./ancestor::figure')[0]
    assert 'article__item--wide' in figure.get('class')


def test_missing_keyword_links_are_replaced(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    keyword = browser.cssselect('.article-tags__link')[5]
    assert keyword.attrib['href'].endswith('/thema/wein')


def test_article_has_print_pdf_function(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    print_m = browser.cssselect('.print-menu__print')
    pdf_m = browser.cssselect('.print-menu__pdf')
    assert (print_m[0].attrib['href'].endswith(
        '/zeit-online/article/01?print=true'))
    assert (pdf_m[0].attrib['href'] ==
            'http://pdf.zeit.de/zeit-online/article/01.pdf')


def test_multi_page_article_has_print_link(testbrowser):
    browser = testbrowser('/zeit-online/article/tagesspiegel')
    print_m = browser.cssselect('.print-menu__print')
    assert (print_m[0].attrib['href'].endswith(
        '/zeit-online/article/tagesspiegel/komplettansicht?print=true'))


def test_article_renders_quotes_correctly(testbrowser):
    browser = testbrowser('/zeit-online/article/quotes')
    quotes = browser.cssselect('.quote')
    assert len(quotes) == 3

    quote_with_linked_source = quotes[0]
    quote_with_source = quotes[1]
    quote_without_source = quotes[2]

    assert quote_with_linked_source.cssselect(
        '.quote__source > .quote__link[href="http://www.imdb.com/title/'
        'tt0110912/quotes?item=qt0447099"]')
    assert not quote_with_source.cssselect('.quote__source > *')
    assert not quote_without_source.cssselect('.quote__source')
