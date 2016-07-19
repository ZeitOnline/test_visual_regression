# -*- coding: utf-8 -*-
import datetime
import pytest
import mock

import zeit.web.core.navigation
import selenium.webdriver

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


def test_nav_markup_should_match_css_selectors(tplbrowser, dummy_request):
    view = mock.MagicMock()
    view.is_advertorial = False
    browser = tplbrowser(
        'zeit.web.site:templates/inc/navigation/navigation.tpl',
        view=view, request=dummy_request)
    html = browser.cssselect

    assert len(html('.header__brand')) == 1
    assert len(html('.nav')) == 1
    assert len(html('.nav > *')) == 6, 'we expect six elements within .nav'
    assert len(html('.header__publisher')) == 1
    assert len(html('.header__menu-link')) == 1
    assert len(html('.header__teaser')) == 1
    assert len(html('.nav__ressorts')) == 1
    assert len(html('.nav__services')) == 1
    assert len(html('.nav__classifieds')) == 1
    assert len(html('.nav__search')) == 1
    assert len(html('.nav__metadata')) == 1
    assert len(html('ul.nav__ressorts-list')) == 1


def test_nav_ressorts_should_produce_markup(tplbrowser, dummy_request):
    view = mock.MagicMock()
    view.request = dummy_request
    nav = zeit.web.core.navigation.NavigationItem('top', '', '')
    nav['hp.global.topnav.links.jobs'] = (
        zeit.web.core.navigation.NavigationItem(
            'hp.global.topnav.links.jobs',
            'Jobs',
            'http://jobs.zeit.de/'))
    nav['hp.global.topnav.links.partnersuche'] = (
        zeit.web.core.navigation.NavigationItem(
            'hp.global.topnav.links.partnersuche',
            'Partnersuche',
            'http://www.zeit.de/angebote/partnersuche/index?pscode=01_100'))
    browser = tplbrowser(
        'zeit.web.site:templates/inc/navigation/navigation-list.tpl',
        view=view, request=dummy_request, navigation=nav,
        nav_class='nav__ressorts')
    html = browser.cssselect

    assert len(html('ul.nav__ressorts-list')) == 1
    assert len(html('ul.nav__ressorts-list > li')) > 1
    assert len(html('ul.nav__ressorts-list > li')) == (
        len(html('ul.nav__ressorts-list > li > a'))), (
            'Links must have same length a list items.')


def test_nav_template_should_render_expected_links(tplbrowser, dummy_request):
    view = mock.MagicMock()
    view.request = dummy_request
    nav = zeit.web.core.navigation.NavigationItem('top', '', '')
    nav['test.epaper'] = (
        zeit.web.core.navigation.NavigationItem(
            'test.epaper',
            'E-Paper',
            'http://foo/epaper'))
    nav['test.audio'] = (
        zeit.web.core.navigation.NavigationItem(
            'test.audio',
            'Audio',
            'http://foo/audio'))
    browser = tplbrowser(
        'zeit.web.site:templates/inc/navigation/navigation-list.tpl',
        view=view, request=dummy_request, navigation=nav,
        nav_class='nav__test')
    links = browser.cssselect('ul.nav__test-list > li > a')

    assert links[0].get('href') == 'http://foo/epaper'
    assert links[1].get('href') == 'http://foo/audio'


def test_nav_contains_essential_elements(tplbrowser, dummy_request):
    view = mock.MagicMock()
    view.package = 'zeit.web.site'

    browser = tplbrowser(
        'zeit.web.site:templates/inc/navigation/navigation.tpl',
        view=view, request=dummy_request)
    html = browser.cssselect
    # Logo
    assert html('a[href*="/index"]'
                '[title="Nachrichten auf ZEIT ONLINE"]')[0] is not None, (
        'Logo link is missing')

    # Main menu icon
    assert len(html(u'a[aria-label="Menü"]')) == 1, (
        'Main menu link is missing')
    assert len(html('svg.header__menu-icon--menu')) == 1, (
        'Main menu icon is missing')

    # Search
    assert len(html('form.search'
                    '[accept-charset="utf-8"]'
                    '[method="get"]'
                    '[role="search"]'
                    '[action$="suche/index"]')) == 1, (
                        'Search form must be present')
    assert len(html('form.search label[for="q"]')) == 1, (
        'Search label must be present')
    assert len(html('button.search__button[type="submit"]')) == 1, (
        'Search button must be present')
    assert len(html('svg.search__icon')) == 1, (
        'Search icon must be present')
    assert len(html('input.search__input[id="q"][name="q"]')) == 1, (
        'Search input must be present')


def test_nav_should_contain_schema_org_markup(tplbrowser, dummy_request):
    view = mock.MagicMock()
    browser = tplbrowser(
        'zeit.web.site:templates/inc/navigation/navigation.tpl',
        view=view, request=dummy_request)
    html = browser.cssselect

    site_nav_element = html(
        '.nav__ressorts[itemtype="http://schema.org/SiteNavigationElement"]')
    assert len(site_nav_element) == 1

    item_prop_url = html('.nav__ressorts a[itemprop="url"]')
    item_prop_name = html('.nav__ressorts span[itemprop="name"]')

    assert len(item_prop_url) > 0
    assert len(item_prop_url) == len(item_prop_name)


def test_footer_should_contain_schema_org_markup(testbrowser):
    browser = testbrowser('/zeit-online/zeitonline')

    site_nav_element = browser.cssselect(
        'footer *[itemtype="http://schema.org/SiteNavigationElement"]')
    assert len(site_nav_element) == 1

    item_prop_url = site_nav_element[0].cssselect('li a[itemprop="url"]')
    item_prop_name = site_nav_element[0].cssselect('li span[itemprop="name"]')

    assert len(item_prop_url) > 0
    assert len(item_prop_url) == len(item_prop_name)


# integration testing

def test_cp_should_have_valid_main_nav_structure(testbrowser):
    browser = testbrowser('/zeit-online/zeitonline')
    html = browser.cssselect

    assert len(html('.nav')) == 1, 'Main navigation must be present'
    assert len(html('.header__logo')) == 1, 'ZON logo must be present'
    assert len(html('.header__menu-link')) == 1, 'Menu link must be present'
    assert len(html('.header__teaser')) == 1, 'Teaser must be present'
    assert len(html('.nav__login')) == 1, 'User profile must be present'


def test_cp_should_have_valid_services_structure(testbrowser):
    browser = testbrowser('/zeit-online/zeitonline')

    links = browser.cssselect('.nav__services a')
    expected = ['E-Paper', 'Audio', 'Apps', 'Archiv']

    assert len(links) == len(expected)

    for link in links:
        assert link.text in expected


def test_cp_should_have_valid_classifieds_structure(testbrowser):
    browser = testbrowser('/zeit-online/zeitonline')

    links = browser.cssselect('.nav__classifieds a')
    expected = ['Abo', 'Shop', 'Akademie', 'Jobs', 'mehr', 'Urlaubsziele',
                'Kulturveranstaltungen', 'Partnersuche', 'Immobilien',
                'Automarkt']

    assert len(links) == len(expected)

    for link in links:
        assert link.text in expected


def test_cp_has_valid_burger_structure(testbrowser):
    browser = testbrowser('/zeit-online/zeitonline')

    assert len(browser.cssselect('svg.header__menu-icon--menu')) == 1, (
        'Main menu burger icon is missing')
    assert len(browser.cssselect('svg.header__menu-icon--close')) == 1, (
        'Main menu close icon is missing')


def test_cp_has_valid_search_structure(testbrowser):
    browser = testbrowser('/zeit-online/zeitonline')
    html = browser.cssselect
    assert len(html('form.search'
                    '[accept-charset="utf-8"]'
                    '[method="get"]'
                    '[role="search"]'
                    '[action$="suche/index"]')) == 1, (
                        'Search form must be present')
    assert len(html('form.search label[for="q"]')) == 1, (
        'Search label must be present')
    assert html('form.search label[for="q"]')[0].text == 'suchen', (
        'Search label has wrong text')
    assert len(html('button.search__button[type="submit"]')) == 1, (
        'Search button must be present')
    assert len(html('svg.search__icon')) == 1, (
        'Search icon must be present')
    assert len(html('input.search__input[id="q"][name="q"]')) == 1, (
        'Search input must be present')


@pytest.fixture(scope='session', params=(
    (320, 480, 1), (520, 960, 1), (768, 1024, 0), (980, 1024, 0)))
def screen_size(request):
    """Run selenium test with multiple screen sizes."""
    return request.param


def test_zon_main_nav_has_correct_structure(
        selenium_driver, testserver, screen_size):

    driver = selenium_driver
    small_screen = screen_size[2]
    screen_width = screen_size[0]
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/index' % testserver.url)

    header = driver.find_element_by_class_name('header')
    nav = header.find_element_by_class_name('nav')
    logo = header.find_element_by_class_name('header__logo')
    menu_link = header.find_element_by_class_name('header__menu-link')
    search_button = nav.find_element_by_class_name('search__button')
    search_input = nav.find_element_by_class_name('search__input')
    nav_login = nav.find_element_by_class_name('nav__login')
    nav_ressorts = nav.find_element_by_class_name('nav__ressorts')
    nav_services = nav.find_element_by_class_name('nav__services')
    nav_classifieds = nav.find_element_by_class_name('nav__classifieds')
    nav_metadata = header.find_element_by_class_name('nav__metadata')
    advertorial_links = nav_ressorts.find_elements_by_class_name(
        'nav__ressorts-item--has-label')

    # header is visible in all sizes
    assert header.is_displayed()
    # logo is visible in all sizes
    assert logo.is_displayed()
    # test advertorial links are present
    assert len(advertorial_links)

    if small_screen:
        # main navigation is hidden
        assert not nav.is_displayed()
        # burger menu is visible
        assert menu_link.is_displayed()
    else:
        # main navigation is visible in desktop mode
        assert nav.is_displayed()
        # search button is visible in desktop mode
        assert search_button.is_displayed()
        # community link is visible in desktop mode
        assert nav_login.is_displayed()
        # ressort bar is visible in desktop mode
        assert nav_ressorts.is_displayed()
        # service bar is visible in desktop mode
        assert nav_services.is_displayed()
        # classifieds bar is visible in desktop mode
        assert nav_classifieds.is_displayed()
        # metadata bar is visible in desktop mode
        assert nav_metadata.is_displayed()

    if screen_width == 768:
        # test search input is hidden in tablet mode
        assert search_input.is_displayed() is False

    # test advertorial links are hidden by default
    for link in advertorial_links:
        assert not link.is_displayed(), 'Advertorial link must be hidden'


def test_nav_search_is_working_as_expected(
        selenium_driver, testserver, screen_size):

    driver = selenium_driver
    screen_width = screen_size[0]
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/zeitonline' % testserver.url)

    driver.execute_script(
        "document.querySelector('.nav__search form').action = location.href")
    driver.execute_script(
        ("document.querySelector('.nav__search .search__input')"
         ".style.transition = 'none'"))

    header = driver.find_element_by_class_name('header')
    menu_link = header.find_element_by_class_name('header__menu-link')
    search__button = header.find_element_by_class_name('search__button')
    search__input = header.find_element_by_class_name('search__input')
    document = driver.find_element_by_class_name('page')
    input_visible_ec = expected_conditions.visibility_of(search__input)
    input_invisible_ec = expected_conditions.invisibility_of_element_located(
        (By.CSS_SELECTOR, ".nav__search .search__input"))

    if screen_width == 768:
        # test search input is shown after button click
        search__button.click()
        # wait for animation
        try:
            WebDriverWait(driver, 1).until(input_visible_ec)
        except TimeoutException:
            assert False, 'Input must be visible'

        # test search input is not hidden after click in input
        search__input.click()
        assert search__input.is_displayed(), 'Input must be visible'

        # test search input is hidden after button click, if its empty
        search__button.click()
        # wait for animation
        try:
            WebDriverWait(driver, 1).until(input_invisible_ec)
        except TimeoutException:
            assert False, 'Input must be hidden'

        # test search input is hidden after click somewhere else, show it first
        search__button.click()
        # wait for animation
        try:
            WebDriverWait(driver, 1).until(input_visible_ec)
        except TimeoutException:
            assert False, 'Input must be visible'
        document.click()
        # wait for animation
        try:
            WebDriverWait(driver, 1).until(input_invisible_ec)
        except TimeoutException:
            assert False, 'Input must be hidden'

    # open search for mobile
    if screen_width < 768:
        menu_link.click()
        # wait for animation
        try:
            WebDriverWait(driver, 1).until(input_visible_ec)
        except TimeoutException:
            assert False, 'Input must be visible'
    # open search for tablet
    elif screen_width == 768:
        search__button.click()
        # wait for animation
        try:
            WebDriverWait(driver, 1).until(input_visible_ec)
        except TimeoutException:
            assert False, 'Input must be visible'

    # test if search form gets submitted
    search__input.send_keys('test')
    search__button.click()

    assert driver.current_url.endswith('/zeit-online/zeitonline?q=test')


def test_nav_burger_menu_is_working_as_expected(selenium_driver, testserver):

    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)

    menu_link = driver.find_element_by_class_name('header__menu-link')
    icon_burger = menu_link.find_element_by_class_name(
        'header__menu-icon--menu')
    icon_close = menu_link.find_element_by_class_name(
        'header__menu-icon--close')

    nav = driver.find_element_by_class_name('nav')
    nav_login = nav.find_element_by_class_name('nav__login')
    nav_ressorts = nav.find_element_by_class_name('nav__ressorts')
    nav_services = nav.find_element_by_class_name('nav__services')
    nav_classifieds = nav.find_element_by_class_name('nav__classifieds')
    nav_search = nav.find_element_by_class_name('nav__search')
    nav_metadata = nav.find_element_by_class_name('nav__metadata')
    advertorial_links = nav_ressorts.find_elements_by_class_name(
        'nav__ressorts-item--has-label')

    # test advertorial links are present
    assert len(advertorial_links)

    # test main elements are displayed
    assert menu_link.is_displayed(), 'Menu button must be visible'
    assert icon_burger.is_displayed(), 'Burger icon must be visible'

    menu_link.click()
    # wait for animation
    try:
        WebDriverWait(driver, 1).until(expected_conditions.visibility_of(nav))
        WebDriverWait(driver, 1).until(expected_conditions.visibility_of(
            nav_services))
    except TimeoutException:
        assert False, 'Navigation must be visible'

    # test element states after menu button is clicked
    assert nav_login.is_displayed(), 'Community must be visible'
    assert nav_metadata.is_displayed(), 'Keywords must be visible'
    assert nav_ressorts.is_displayed(), 'Ressorts must be visible'
    assert nav_services.is_displayed(), 'Services must be visible'
    assert nav_classifieds.is_displayed(), 'Classifieds must be visible'
    assert nav_search.is_displayed(), 'Search must be visible'

    for link in advertorial_links:
        assert link.is_displayed(), 'Advertorial link must be visible'

    # test close button is displayed
    assert icon_close.is_displayed(), 'Closing Icon is not displayed'

    menu_link.click()
    # wait for animation
    try:
        WebDriverWait(driver, 1).until(
            expected_conditions.invisibility_of_element_located(
                (By.CSS_SELECTOR, ".nav")))
    except TimeoutException:
        assert False, 'Navigation must be hidden'

    # test element states after menu button is clicked again
    assert not nav_login.is_displayed(), 'Community must be hidden'
    assert not nav_metadata.is_displayed(), 'Keywords must be hidden'
    assert not nav_ressorts.is_displayed(), 'Ressorts must be hidden'
    assert not nav_services.is_displayed(), 'Services must be hidden'
    assert not nav_classifieds.is_displayed(), 'Classifieds must be hidden'
    assert not nav_search.is_displayed(), 'Search must be hidden'

    for link in advertorial_links:
        assert not link.is_displayed(), 'Advertorial link must be visible'


def test_primary_nav_should_resize_to_fit(selenium_driver, testserver):

    driver = selenium_driver
    actions = selenium.webdriver.ActionChains(driver)
    driver.get('%s/zeit-online/zeitonline' % testserver.url)

    # mobile
    driver.set_window_size(320, 480)

    ressorts = driver.find_element_by_class_name('nav__ressorts')
    more_dropdown = ressorts.find_element_by_css_selector(
        '.nav__ressorts-item--more')
    chosen_nav_item = ressorts.find_elements_by_css_selector(
        '.nav__ressorts-list > li > a')[9]
    cloned_nav_item = more_dropdown.find_elements_by_css_selector(
        '.nav__dropdown-list > li > a')[9]
    featured_nav_item = ressorts.find_element_by_class_name(
        'nav__ressorts-item--featured')
    menu_link = driver.find_element_by_class_name('header__menu-link')

    assert chosen_nav_item.get_attribute('textContent') == 'Sport'

    menu_link.click()
    # wait for animation
    try:
        WebDriverWait(driver, 1).until(
            expected_conditions.visibility_of(chosen_nav_item))
    except TimeoutException:
        assert False, 'Navigation item must be visible'

    assert not more_dropdown.is_displayed(), (
        '[on mobile] more dropdown is not displayed')
    assert chosen_nav_item.is_displayed(), (
        '[on mobile] chosen nav item should be visible in open navigation')

    # tablet
    driver.set_window_size(768, 1024)
    # wait for script
    try:
        WebDriverWait(driver, 1).until(
            expected_conditions.visibility_of(featured_nav_item))
    except TimeoutException:
        assert False, 'Featured item must be visible'

    assert not chosen_nav_item.is_displayed(), (
        '[on tablet] chosen nav item should be hidden')
    assert more_dropdown.is_displayed(), (
        '[on tablet] more dropdown should be visible')
    actions.move_to_element(more_dropdown).perform()
    assert cloned_nav_item.is_displayed(), (
        '[on tablet] chosen nav item should be visible'
        ' in more-dropdown on :hover')

    # desktop
    driver.set_window_size(980, 1024)
    # wait for animation
    try:
        WebDriverWait(driver, 1).until(
            expected_conditions.visibility_of(chosen_nav_item))
    except TimeoutException:
        assert False, 'Navigation item must be visible'

    assert chosen_nav_item.is_displayed(), (
        '[on desktop] chosen nav item should be visible')


def test_zmo_link_exists_and_is_clickable(selenium_driver, testserver):

    driver = selenium_driver
    driver.set_window_size(1024, 768)
    driver.get('%s/zeit-online/zeitonline' % testserver.url)

    zmo_button = driver.find_element_by_class_name(
        'nav__ressorts-item--featured')
    zmo_link = zmo_button.find_element_by_tag_name('a')

    assert zmo_link.get_attribute('href') == '{}/zeit-magazin/index'.format(
        testserver.url
    ), 'zmo link is not set correctly'

    zmo_link.click()

    assert driver.current_url == '{}/zeit-magazin/index'.format(
        testserver.url), 'zmo hp wasnt called correctly'


def test_nav_hp_contains_relative_date(tplbrowser, dummy_request):
    def now(**kwargs):
        return datetime.datetime.now() - datetime.timedelta(**kwargs)

    view = mock.MagicMock()
    view.is_hp = True
    view.date_last_modified = now(hours=1)
    browser = tplbrowser(
        'zeit.web.site:templates/inc/navigation/navigation.tpl',
        view=view, request=dummy_request)
    header_date = browser.cssselect('.nav__date')

    assert len(header_date) == 1
    assert header_date[0].text_content().strip() == 'Aktualisiert vor 1 Stunde'

    view.date_last_modified = now(hours=3)
    browser = tplbrowser(
        'zeit.web.site:templates/inc/navigation/navigation.tpl',
        view=view, request=dummy_request)
    header_date = browser.cssselect('.nav__date')

    assert len(header_date) == 0
