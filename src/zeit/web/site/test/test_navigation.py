# -*- coding: utf-8 -*-
import datetime
import lxml
import pytest
import mock

import zeit.web.core.navigation
import selenium.webdriver

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


def test_nav_markup_should_match_css_selectors(application, jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/navigation/navigation.tpl')
    mock_view = mock.MagicMock()
    mock_request = mock.Mock()
    mock_request.route_url.return_value = 'http://www.zeit.de/'
    mock_view.request = mock_request
    mock_request.registry.settings.sso_activate = False
    mock_view.is_advertorial = False
    html_str = tpl.render(view=mock_view, request=mock_request)
    html = lxml.html.fromstring(html_str).cssselect

    assert len(html('.main_nav')) == 1, 'just one .main_nav should be present'

    assert len(html('.main_nav > div')) == 7, 'seven divs within .main_nav'

    assert len(html('.main_nav > div.logo_bar >'
                    'h1.logo_bar__brand')) == 1, 'just one .logo_bar__brand'

    assert len(html('.main_nav > div.logo_bar >'
                    'div.logo_bar__menu')) == 1, 'just one .logo_bar__menu'

    assert len(html('.main_nav > div.main_nav__teaser')) == 1, (
        'just one .main_nav__teaser')

    assert len(html('.main_nav > div.main_nav__ressorts'
                    '[data-dropdown="true"]')
               ) == 1, 'just one .main_nav__ressorts w/ data-dropdown=true'

    assert len(html('.main_nav > div.main_nav__services'
                    '[data-dropdown="true"]')
               ) == 1, 'just one .main_nav__services w/ data-dropdown=true'

    assert len(html('.main_nav > div.main_nav__classifieds'
                    '[data-dropdown="true"]')
               ) == 1, 'just one .main_nav__classifieds w/ data-dropdown=true'

    assert len(html('.main_nav > div.main_nav__search'
                    '[data-dropdown="true"]')
               ) == 1, 'just one .main_nav__search w/ data-dropdown=true'

    assert len(html('nav[role="navigation"] ul.primary-nav')) == 1


def test_nav_ressorts_should_produce_markup(application, jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/navigation/navigation-list.tpl')
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
    mock_view = mock.Mock()
    mock_request = mock.Mock()
    mock_request.route_url.return_value = 'http://www.zeit.de/'
    mock_view.request = mock_request
    html_str = tpl.render(view=mock_view,
                          request=mock_request,
                          navigation=nav, nav_class='primary-nav')
    html = lxml.html.fromstring(html_str).cssselect

    assert len(html('ul.primary-nav')) == 1
    assert len(html('ul li.primary-nav__item')) > 1
    assert len(html('ul li.primary-nav__item a.primary-nav__link')) == (
        len(html('ul li.primary-nav__item'))), (
            'Links must have same length a list items.')


def test_nav_services_should_have_expected_links(application, jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/navigation/navigation-list.tpl')
    nav = zeit.web.core.navigation.NavigationItem('top', '', '')
    nav['topnav.services.1..epaper'] = (
        zeit.web.core.navigation.NavigationItem(
            'topnav.services.1..epaper',
            'E-Paper',
            'https://premium.zeit.de/?wt_mc=pm.intern.fix.\
            zeitde.fix.dach.text.epaper'))
    nav['topnav.services.2..audio'] = (
        zeit.web.core.navigation.NavigationItem(
            'topnav.services.2..audio',
            'Audio',
            'https://premium.zeit.de/abo/digitalpaket5?wt_mc=pm.intern.fix.\
            zeitde.fix.dach.text.audio'))
    mock_view = mock.Mock()
    mock_request = mock.Mock()
    mock_request.route_url.return_value = 'http://www.zeit.de/'
    mock_view.request = mock_request
    html_str = tpl.render(view=mock_view,
                          navigation=nav, nav_class='primary-nav-services')
    html = lxml.html.fromstring(html_str).cssselect

    assert (html('li > a[href^="https://premium.zeit.de/?wt_mc=pm.intern"]')[0]
            is not None), 'No link for epaper'
    assert (html('li > a[href^="https://premium.zeit.de/abo/digitalpaket"]')[0]
            is not None), 'No link audio'


def test_nav_classifieds_should_have_expected_links(application, jinja2_env):
    nav = zeit.web.core.navigation.NavigationItem('top', '', '')
    nav['topnav.classifieds.3..jobs'] = (
        zeit.web.core.navigation.NavigationItem(
            'topnav.classifieds.3..jobs',
            'Jobs',
            'http://jobs.zeit.de/'))
    nav['topnav.classifieds.4..partnersuche'] = (
        zeit.web.core.navigation.NavigationItem(
            'topnav.classifieds.4..partnersuche',
            'Partnersuche',
            'http://www.zeit.de/angebote/partnersuche/index?pscode=01_100'))
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/navigation/navigation-list.tpl')
    mock_view = mock.Mock()
    mock_request = mock.Mock()
    mock_request.route_url.return_value = 'http://www.zeit.de/'
    mock_view.request = mock_request
    html_str = tpl.render(view=mock_view,
                          navigation=nav, nav_class='main-nav-classifieds')
    html = lxml.html.fromstring(html_str).cssselect

    assert html('li > a[href^="http://jobs.zeit.de/"]')[0] is not None, (
        'No link for zeit jobs')
    assert html('li > a[href*="zeit.de/angebote/partner"]')[0] is not None, (
        'Link for partnersuche not present')


def test_nav_contains_essential_elements(application, jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/navigation/navigation.tpl')
    mock_view = mock.MagicMock()
    mock_view.package = 'zeit.web.site'

    def route_url(arg):
        return 'http://www.zeit.de/'

    mock_request = mock.Mock()
    mock_request.route_url = route_url
    html_str = tpl.render(view=mock_view, request=mock_request)
    html = lxml.html.fromstring(html_str).cssselect
    # Logo
    assert html('a[href*="/index"]'
                '[title="Nachrichten auf ZEIT ONLINE"]')[0] is not None, (
        'Logo link is missing')

    # Main menu icon
    assert len(html(u'a[aria-label="Hauptmenü"]')) == 1, (
        'Main menu link is missing')
    assert len(html('svg.logo_bar__menu-icon--burger')) == 1, (
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


def test_nav_should_contain_schema_org_markup(application, jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/navigation/navigation.tpl')
    mock_view = mock.MagicMock()
    mock_view.request.route_url.return_value = 'http://www.zeit.de/'
    mock_request = mock.Mock()
    html_str = tpl.render(view=mock_view, request=mock_request)
    html = lxml.html.fromstring(html_str).cssselect

    site_nav_element = html(
        '.main_nav__ressorts ul'
        '[itemtype="http://schema.org/SiteNavigationElement"]')
    assert len(site_nav_element) == 1

    item_prop_url = html(
        '.main_nav__ressorts '
        'ul[itemtype="http://schema.org/SiteNavigationElement"] '
        'li a[itemprop="url"]')
    item_prop_name = html(
        '.main_nav__ressorts '
        'ul[itemtype="http://schema.org/SiteNavigationElement"] li '
        'a[itemprop="url"] span[itemprop="name"]')

    assert len(item_prop_url) > 0
    assert len(item_prop_url) == len(item_prop_name)


def test_footer_should_contain_schema_org_markup(testbrowser):
    browser = testbrowser('/centerpage/zeitonline')

    html = browser.cssselect
    site_nav_element = html(
        'footer[itemtype="http://schema.org/SiteNavigationElement"]')
    assert len(site_nav_element) == 1

    item_prop_url = html(
        'footer[itemtype="http://schema.org/SiteNavigationElement"] '
        'div li a[itemprop="url"]')
    item_prop_name = html(
        'footer[itemtype="http://schema.org/SiteNavigationElement"] div li '
        'a[itemprop="url"] span[itemprop="name"]')

    assert len(item_prop_url) > 0
    assert len(item_prop_url) == len(item_prop_name)


# integration testing

def test_cp_should_have_valid_main_nav_structure(testbrowser):
    browser = testbrowser('/centerpage/zeitonline')
    html = browser.cssselect

    assert len(html('.main_nav')) == 1, 'Main navigation must be present'
    assert len(html('.logo_bar__brand-logo')) == 1, (
        'ZON logo must be present')
    assert len(html('div.logo_bar__menu')) == 1, 'Menu link must be present'
    assert len(html('div.main_nav__teaser')) == 1, 'Teaser must be present'
    assert len(html('div.main_nav__community')) == 1, (
        'User profile must be present')


def test_cp_should_have_valid_services_structure(testbrowser):
    browser = testbrowser('/centerpage/zeitonline')
    html = browser.cssselect

    assert len(html('li[data-id="epaper"]')) == 1, (
        'Epaper link not present.')
    assert len(html('li[data-id="audio"]')) == 1, (
        'Audio link not present.')
    assert len(html('li[data-id="apps"]')) == 1, (
        'Apps link not present.')
    assert len(html('li[data-id="archiv"]')) == 1, (
        'Archiv link not present.')


def test_cp_should_have_valid_classifieds_structure(testbrowser):
    browser = testbrowser('/centerpage/zeitonline')
    html = browser.cssselect

    assert len(html('li[data-id="abo"] > a')) == 1, (
        'Abo link is not present.')
    assert len(html('li[data-id="shop"] > a')) == 1, (
        'Shop link is not present.')
    assert len(html('li[data-id="akademie"] > a')) == 1, (
        'Akademie link is not present.')
    assert len(html('li[data-id="jobs"] > a')) == 1, (
        'Job link is not present.')
    assert len(html('li[data-id="urlaubsziele"] > a')) == 2, (
        'Urlaubsziele link is not present.')
    assert len(html('li[data-id="kulturveranstaltungen"] > a')) == 2, (
        'Kulturveranstaltungen link is not present.')
    assert len(html('li[data-id="partnersuche"] > a')) == 2, (
        'Partnersuche link is not present.')
    assert len(html('li[data-id="immobilien"] > a')) == 2, (
        'Immo link is not present.')
    assert len(html('li[data-id="automarkt"] > a')) == 2, (
        'Automarkt link is not present.')


def test_cp_has_valid_burger_structure(testbrowser):
    browser = testbrowser('/centerpage/zeitonline')
    html_str = browser.contents
    html = lxml.html.fromstring(html_str).cssselect
    assert len(html('svg.logo_bar__menu-icon--burger')) == 1, (
        'Main menu burger icon is missing')
    assert len(html('svg.logo_bar__menu-icon--close')) == 1, (
        'Main menu close icon is missing')


def test_cp_has_valid_search_structure(testbrowser):
    browser = testbrowser('/centerpage/zeitonline')
    html_str = browser.contents
    html = lxml.html.fromstring(html_str).cssselect
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

    main_nav = driver.find_elements_by_class_name('main_nav')[0]
    logo_bar__logo = driver.find_elements_by_class_name(
        'logo_bar__brand-logo')[0]
    search__button = driver.find_elements_by_class_name('search__button')[0]
    search__input = driver.find_elements_by_class_name('search__input')[0]
    main_nav__community = driver.find_elements_by_class_name(
        'main_nav__community')[0]
    logo_bar__menu = driver.find_elements_by_class_name('logo_bar__menu')[0]
    main_nav__ressorts = driver.find_elements_by_class_name(
        'main_nav__ressorts')[0]
    header__tags = driver.find_elements_by_class_name('header__tags')[0]
    header_metadata = driver.find_elements_by_class_name('header__metadata')[0]
    main_nav__services = driver.find_elements_by_class_name(
        'main_nav__services')[0]
    main_nav__classifieds = driver.find_elements_by_class_name(
        'main_nav__classifieds')[0]

    # navigation is visible in all sizes
    assert main_nav.is_displayed()
    # logo is visible in all sizes
    assert logo_bar__logo.is_displayed()

    if small_screen:
        # burger menu is visible
        assert logo_bar__menu.is_displayed()
        # tags are hidden
        assert header__tags.is_displayed() is False
        # date bar is hidden
        assert header_metadata.is_displayed() is False
        # services li hidden from 4th elem on
        serv_li = main_nav__services.find_elements_by_tag_name('li')
        for li in serv_li[:3]:
            assert li.is_displayed() is False
    else:
        # search button is visible in desktop mode
        assert search__button.is_displayed()
        # community link is visible in desktop mode
        assert main_nav__community.is_displayed()
        # ressort bar is visible in desktop mode
        assert main_nav__ressorts.is_displayed()
        # service bar is visible in desktop mode
        assert main_nav__services.is_displayed()
        # classifieds bar is visible in desktop mode
        assert main_nav__classifieds.is_displayed()

    if screen_width == 768:
        # test search input is hidden in tablet mode
        assert search__input.is_displayed() is False


def test_nav_search_is_working_as_expected(
        selenium_driver, testserver, screen_size):

    driver = selenium_driver
    screen_width = screen_size[0]
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/centerpage/zeitonline' % testserver.url)

    driver.execute_script(
        "document.querySelector('.main_nav__search form').action = \
            location.href")
    driver.execute_script(
        ("document.querySelector('.main_nav__search .search__input')"
         ".style.transition = 'none'"))

    search__button = driver.find_elements_by_class_name('search__button')[0]
    search__input = driver.find_elements_by_class_name('search__input')[0]
    logo_bar__menu = driver.find_element_by_class_name('logo_bar__menu')
    menu__button = logo_bar__menu.find_elements_by_tag_name('a')[0]
    document = driver.find_element_by_class_name('page')
    input_visible_ec = expected_conditions.visibility_of(search__input)
    input_invisible_ec = expected_conditions.invisibility_of_element_located(
        (By.CSS_SELECTOR, ".main_nav__search .search__input"))

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
        menu__button.click()
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

    assert driver.current_url.endswith('/centerpage/zeitonline?q=test')


def test_nav_burger_menu_is_working_as_expected(selenium_driver, testserver):

    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/centerpage/zeitonline' % testserver.url)

    logo_bar__menu = driver.find_element_by_class_name('logo_bar__menu')
    menu_link = logo_bar__menu.find_element_by_tag_name('a')
    icon_burger = logo_bar__menu.find_element_by_class_name(
        'logo_bar__menu-icon--burger')
    icon_close = logo_bar__menu.find_element_by_class_name(
        'logo_bar__menu-icon--close')

    main_nav__community = driver.find_element_by_class_name(
        'main_nav__community')
    main_nav__ressorts = driver.find_element_by_class_name(
        'main_nav__ressorts')
    main_nav__services = driver.find_element_by_class_name(
        'main_nav__services')
    main_nav__classifieds = driver.find_element_by_class_name(
        'main_nav__classifieds')
    main_nav__search = driver.find_element_by_class_name('main_nav__search')

    # test main elements are displayed
    assert logo_bar__menu.is_displayed(), 'Logo bar is not displayed'
    assert menu_link.is_displayed(), 'menu button is not displayed'
    assert icon_burger.is_displayed(), 'Burger Icon is not displayed'

    menu_link.click()

    # test element states after menu button is clicked
    assert main_nav__community.is_displayed(), (
        'Community bar is not displayed')
    assert main_nav__ressorts.is_displayed(), (
        'Ressort bar is not displayed')
    assert main_nav__services.is_displayed(), (
        'Services bar is not displayed')
    assert main_nav__classifieds.is_displayed(), (
        'Classifieds bar is not displayed')
    assert main_nav__search.is_displayed(), (
        'Search bar is not displayed')

    # test close button is displayed
    assert icon_close.is_displayed(), 'Closing Icon is not displayed'

    menu_link.click()

    # test element states after menu button is clicked again
    assert main_nav__community.is_displayed() is False, (
        'Community bar is displayed')
    assert main_nav__ressorts.is_displayed() is False, (
        'Ressorts bar is displayed')
    assert main_nav__services.is_displayed() is False, (
        'Services bar is displayed')
    assert main_nav__classifieds.is_displayed() is False, (
        'Classifieds bar is displayed')
    assert main_nav__search.is_displayed() is False, (
        'Search bar is displayed')


def test_advertorial_nav_links_hidden_mobile(selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)

    logo_bar__menu = driver.find_element_by_class_name('logo_bar__menu')
    menu_link = logo_bar__menu.find_element_by_tag_name('a')
    ressort_nav = driver.find_element_by_class_name(
        'main_nav__ressorts')
    adv_links = ressort_nav.find_elements_by_class_name(
        'primary-nav__item--has-label')

    menu_link.click()

    # test navigation is display, advertorials not
    assert ressort_nav.is_displayed(), 'Ressort bar is not displayed'
    assert len(adv_links) == 2, 'advertorial links missing'
    assert not adv_links[0].is_displayed(), 'advertorial links are displayed'


def test_primary_nav_should_resize_to_fit(selenium_driver, testserver):

    driver = selenium_driver
    actions = selenium.webdriver.ActionChains(driver)
    driver.get('%s/centerpage/zeitonline' % testserver.url)

    # mobile
    driver.set_window_size(320, 480)

    more_dropdown = driver.find_element_by_css_selector(
        '[data-id="more-dropdown"]')
    chosen_nav_item = driver.find_element_by_css_selector(
        '[data-id="sport"]')
    chosen_more_dropdown_item = driver.find_element_by_css_selector(
        '[data-id="more-dropdown"] [data-id="sport"]')

    logo_bar__menu = driver.find_element_by_class_name('logo_bar__menu')
    menu__button = logo_bar__menu.find_elements_by_tag_name('a')[0]
    menu__button.click()

    assert more_dropdown.is_displayed() is False, (
        '[on mobile] more dropdown is not displayed')
    assert chosen_nav_item.is_displayed(), (
        '[on mobile] chosen nav item should be visible in open navigation')

    # tablet
    driver.set_window_size(768, 1024)

    assert chosen_nav_item.is_displayed() is False, (
        '[on tablet] chosen nav item should be hidden')
    actions.move_to_element(more_dropdown).perform()
    assert chosen_more_dropdown_item.is_displayed(), (
        '[on tablet] chosen nav item should be visible'
        ' in more-dropdown on :hover')

    # desktop
    driver.set_window_size(980, 1024)

    assert chosen_nav_item.is_displayed(), (
        '[on desktop] chosen nav item should be visible')


def test_zmo_link_exists_and_is_clickable(selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/centerpage/zeitonline' % testserver.url)

    zmo_button = driver.find_element_by_class_name(
        'primary-nav__item--featured')
    zmo_link = zmo_button.find_element_by_class_name(
        'primary-nav__link')

    assert zmo_link.get_attribute('href') == '{}/zeit-magazin/index'.format(
        testserver.url
    ), 'zmo link is not set correctly'
    assert (zmo_link.get_attribute('data-id') ==
            'topnav.mainnav.14..zeitmagazin'), (
        'zmo tracking is not set correctly')

    zmo_link.click()

    assert driver.current_url == '{}/zeit-magazin/index'.format(
        testserver.url), 'zmo hp wasnt called correctly'


def test_nav_hp_contains_relative_date(jinja2_env):
    def now(**kwargs):
        return datetime.datetime.now() - datetime.timedelta(**kwargs)

    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/centerpage.html')
    view = mock.Mock()
    view.is_hp = True
    view.date_last_modified = now(hours=1)
    lines = tpl.blocks['metadata'](tpl.new_context({'view': view}))
    html_str = ' '.join(lines).strip()
    html = lxml.html.fromstring(html_str)
    header_date = html.cssselect('.header__date')

    assert len(header_date) == 1
    assert header_date[0].text_content().strip() == 'Aktualisiert vor 1 Stunde'

    view.date_last_modified = now(hours=3)
    lines = tpl.blocks['metadata'](tpl.new_context({'view': view}))
    html_str = ' '.join(lines).strip()
    html = lxml.html.fromstring(html_str)
    header_date = html.cssselect('.header__date')

    assert len(header_date) == 0
