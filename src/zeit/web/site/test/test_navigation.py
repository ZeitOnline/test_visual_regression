# -*- coding: utf-8 -*-
import datetime
import time
import lxml
import pytest
import mock

import zeit.web.core.navigation
import selenium.webdriver


def test_nav_markup_should_match_css_selectors(application, jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/navigation/navigation.tpl')
    mock_view = mock.MagicMock()
    mock_request = mock.Mock()
    mock_request.route_url.return_value = 'http://www.zeit.de/'
    mock_view.request = mock_request
    html_str = tpl.render(view=mock_view)
    html = lxml.html.fromstring(html_str).cssselect

    assert len(html('.main_nav')) == 1, 'just one .main_nav should be present'

    assert len(html('.main_nav > div')) == 8, 'seven divs within .main_nav'

    assert len(html('.main_nav > div.logo_bar >'
                    'h1.logo_bar__image')) == 1, 'just one .logo_bar__image'

    assert len(html('.main_nav > div.logo_bar >'
                    'div.logo_bar__menue')) == 1, 'just one .logo_bar__menue'

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
    nav = zeit.web.core.navigation.Navigation()
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
    nav = zeit.web.core.navigation.Navigation()
    nav['abo'] = (
        zeit.web.core.navigation.NavigationItem(
            'abo',
            'Abo',
            'http://www.zeitabo.de/?mcwt=2009_07_0002'))
    nav['hp.global.topnav.links.shop'] = (
        zeit.web.core.navigation.NavigationItem(
            'hp.global.topnav.links.shop',
            'Shop',
            'http://shop.zeit.de?et=l6VVNm&et_cid=42&et_lid=175'))
    mock_view = mock.Mock()
    mock_request = mock.Mock()
    mock_request.route_url.return_value = 'http://www.zeit.de/'
    mock_view.request = mock_request
    html_str = tpl.render(view=mock_view,
                          navigation=nav, nav_class='primary-nav-services')
    html = lxml.html.fromstring(html_str).cssselect

    assert html('li > a[href="http://www.zeitabo.de/'
                '?mcwt=2009_07_0002"]')[0] is not None, 'No link for zeit abo'
    assert html('li[data-id="hp.global.topnav.links.shop"]'
                '> a[href="http://shop.zeit.de?et=l6VVNm&et_cid=42&'
                'et_lid=175"]')[0] is not None, 'No link for shop zeit'


def test_nav_classifieds_should_have_expected_links(application, jinja2_env):
    nav = zeit.web.core.navigation.Navigation()
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
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/navigation/navigation-list.tpl')
    mock_view = mock.Mock()
    mock_request = mock.Mock()
    mock_request.route_url.return_value = 'http://www.zeit.de/'
    mock_view.request = mock_request
    html_str = tpl.render(view=mock_view,
                          navigation=nav, nav_class='main-nav-classifieds')
    html = lxml.html.fromstring(html_str).cssselect

    assert html('li[data-id="hp.global.topnav.links.jobs"]'
                '> a[href="http://jobs.zeit.de/"]'
                '')[0] is not None, 'No link for zeit jobs'
    assert html('li[data-id="hp.global.topnav.links.partnersuche"]'
                '> a[href="http://www.zeit.de/angebote/partnersuche/index?'
                'pscode=01_100"]')[0] is not None, (
                    'Link for partnersuche not present')


def test_nav_contains_essential_elements(application, jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/navigation/navigation.tpl')
    mock_view = mock.MagicMock()
    mock_view.request.host = 'www.zeit.de'
    html_str = tpl.render(view=mock_view)
    html = lxml.html.fromstring(html_str).cssselect

    # Logo
    assert html('a[href*="/index"]'
                '[title="Nachrichten auf ZEIT ONLINE"]'
                '[class="icon-zon-logo-desktop"]'
                '[id="hp.global.topnav.centerpages.logo"]')[0] is not None, (
                    'Logo link is missing')

    # Main menu icon
    assert html(u'a[aria-label="Hauptmenü"]')[0] is not None, (
        'Main menu link is missing')
    assert len(html('div.logo_bar__menue__image.main_nav__icon--plain'
                    '.icon-zon-logo-navigation_menu')) == 1, (
                        'Logo for bar menu is not present')
    assert len(html('div.logo_bar__menue__image'
                    '.main_nav__icon--hover.icon-zon-logo-'
                    'navigation_menu-hover')) == 1, (
                        'A div for the burger menu is missing.')

    # Search
    assert html('form.search'
                '[accept-charset="utf-8"]'
                '[method="get"]'
                '[role="search"]'
                '[action$="suche/index"]')[0] is not None, (
                    'Form element is not present')
    assert html('label.hideme[for="q"]')[0] is not None, (
        'Hide me label is not present')
    assert html('button.search__button[type="submit"]')[0] is not None, (
        'No search button present')
    assert html('span.icon-zon-logo-navigation_suche'
                '.search__button__image.'
                'main_nav__icon--plain')[0] is not None, (
                    'No search logo present')
    assert html('span.icon-zon-logo-navigation_suche-hover'
                '.search__button__image.'
                'main_nav__icon--hover')[0] is not None, (
                    'No icon-hover present')
    assert html('input.search__input[id="q"][name="q"]'
                '[type="search"][placeholder="Suche"]')[0] is not None, (
                    'No search input present')


def test_nav_should_contain_schema_org_markup(application, jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/navigation/navigation.tpl')
    mock_view = mock.MagicMock()
    mock_view.request.host = 'www.zeit.de'
    html_str = tpl.render(view=mock_view)
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


def test_footer_should_contain_schema_org_markup(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)

    html = browser.cssselect
    site_nav_element = html(
        'footer[itemtype="http://schema.org/SiteNavigationElement"]')
    assert len(site_nav_element) == 1

    item_prop_url = html(
        'footer[itemtype="http://schema.org/SiteNavigationElement"] '
        'li a[itemprop="url"]')
    item_prop_name = html(
        'footer[itemtype="http://schema.org/SiteNavigationElement"] li '
        'a[itemprop="url"] span[itemprop="name"]')

    assert len(item_prop_url) > 0
    assert len(item_prop_url) == len(item_prop_name)


# integration testing

def test_cp_should_have_valid_main_nav_structure(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    html = browser.cssselect

    assert len(html('.main_nav')) == 1, 'Nav main_nav is not present.'
    assert len(html('div.logo_bar__image')) == 1, 'Logo bar image not present.'
    assert len(html('div.logo_bar__menue')) == 1, 'Menu bar is not present.'
    assert len(html('div.main_nav__teaser')) == 1, 'Nav teaser not present.'
    assert len(html('div.main_nav__community[data-dropdown="true"]')) == 1, (
        'Data dropdown not present')


def test_cp_should_have_valid_services_structure(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    html = browser.cssselect

    assert len(html('li[data-id="hp.global.topnav.links.abo"]')) == 1, (
        'Abo link not present.')
    assert len(html('li[data-id="hp.global.topnav.links.shop"]')) == 1, (
        'Shop link is not present')
    assert len(html('li[data-id="hp.global.topnav.links.audio"]')) == 1, (
        'Audio link is not present.')
    assert len(html('li[data-id="hp.global.topnav.links.apps"]')) == 1, (
        'App link is not present.')
    assert len(html('li[data-id="hp.global.topnav.links.archiv"]')) == 1, (
        'Archiv link is not present')


def test_cp_should_have_valid_classifieds_structure(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    html = browser.cssselect

    assert len(html('li[data-id="hp.global.topnav.links.jobs"] > a')) == 1, (
        'Job link is not present.')
    assert len(html(
        'li[data-id="hp.global.topnav.links.partnersuche"] > a')) == 1, (
            'Link partnersuche is not present.')
    assert len(html('li[data-id="hp.global.topnav.links.mehr"] > a')) == 1, (
        'Link mehr is not present')


def test_cp_has_valid_community_structure(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    html_str = browser.contents
    html = lxml.html.fromstring(html_str).cssselect
    assert html(
        'a[href="http://community.zeit.de/user/login?"]') is not None, (
            'Link to login form is invalid')
    assert html('span.main_nav__community__image') is not None, (
        'span.main_nav__community__image is invalid')


def test_cp_has_valid_logo_structure(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    html_str = browser.contents
    html = lxml.html.fromstring(html_str).cssselect
    assert html('a.icon-zon-logo-desktop'
                '[href="http://www.zeit.de/index"]'
                '[title="Nachrichten auf ZEIT ONLINE"]'
                '[id="hp.global.topnav.centerpages.logo"]') is not None, (
                    'Element a.icon-zon-logo-desktop is invalid')


def test_cp_has_valid_burger_structure(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    html_str = browser.contents
    html = lxml.html.fromstring(html_str).cssselect
    assert html('div.logo_bar__menue__image'
                '.main_nav__icon--plain'
                '.icon-zon-logo-navigation_menu') is not None, (
                    'Element div.main_nav__icon--plain is invalid')
    assert html('div.logo_bar__menue__image'
                '.main_nav__icon--hover'
                '.icon-zon-logo-navigation_menu-hover') is not None, (
                    'Element .main_nav__icon--hover is invalid')


def test_cp_has_valid_search_structure(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    html_str = browser.contents
    html = lxml.html.fromstring(html_str).cssselect
    assert html('form.search'
                '[accept-charset="utf-8"]'
                '[method="get"]'
                '[role="search"]'
                '[action$="suche/index"]') is not None, (
                    'Element form.search is invalid')
    assert html('label.hideme[for="q"]') is not None, (
        'label.hideme is invalid')
    assert html('label.hideme[for="q"]')[0].text == 'suchen', (
        'Element label.hideme has wrong text')
    assert html('button.search__button'
                '[type="submit"]'
                '[tabindex="2"]') is not None, (
                    'Element button.search__button is invalid')
    assert html('span.icon-zon-logo-navigation_suche.search__button__image'
                '.main_nav__icon--plain') is not None, (
                    'Element span in invalid')
    assert html('span.icon-zon-logo-navigation_suche-hover'
                '.search__button__image'
                '.main_nav__icon--hover')[0].text is None, (
                    'Element span is not empty')
    assert html('input.search__input'
                '[id="q"]'
                '[name="q"]'
                '[type="search"]'
                '[placeholder="Suche"]'
                '[tabindex="1"]') is not None, (
                    'Element input.search__input is invalid')


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
    logo_bar__image = driver.find_elements_by_class_name('logo_bar__image')[0]
    search__button = driver.find_elements_by_class_name('search__button')[0]
    search__input = driver.find_elements_by_class_name('search__input')[0]
    main_nav__community = driver.find_elements_by_class_name(
        'main_nav__community')[0]
    logo_bar__menue = driver.find_elements_by_class_name('logo_bar__menue')[0]
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
    assert logo_bar__image.is_displayed()

    if small_screen:
        # burger menue is visible
        assert logo_bar__menue.is_displayed()
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

    search__button = driver.find_elements_by_class_name('search__button')[0]
    search__input = driver.find_elements_by_class_name('search__input')[0]
    logo_bar__menue = driver.find_element_by_class_name('logo_bar__menue')
    menue__button = logo_bar__menue.find_elements_by_tag_name('a')[0]
    document = driver.find_element_by_class_name('page')
    transition_duration = 0.2

    if screen_width == 768:
        # test search input is shown after button click
        search__button.click()
        time.sleep(transition_duration)  # wait for animation
        assert search__input.is_displayed(), 'Input is not displayed'
        # test search input is not hidden after click in input
        search__input.click()
        assert search__input.is_displayed(), 'Input is not displayed'
        # test search input is hidden after button click, if its empty
        search__button.click()
        time.sleep(transition_duration)  # wait for animation
        assert search__input.is_displayed() is False, 'Input is displayed'
        # test search input is hidden after click somewhere else, show it first
        search__button.click()
        time.sleep(transition_duration)  # wait for animation
        document.click()
        time.sleep(transition_duration)  # wait for animation
        assert search__input.is_displayed() is False, 'Input is displayed'

    # open search for mobile
    if screen_width < 768:
        menue__button.click()
    # open search for tablet
    elif screen_width == 768:
        search__button.click()
        time.sleep(transition_duration)  # wait for animation

    # test if search is performed
    search__input.send_keys('test')
    search__button.click()

    assert driver.current_url.endswith('suche/index?q=test')


@pytest.mark.xfail(reason='Maybe a problem with tear down. Runs isolated.')
def test_nav_burger_menue_is_working_as_expected(
        selenium_driver, testserver):

    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/centerpage/zeitonline' % testserver.url)

    logo_bar__menue = driver.find_element_by_class_name('logo_bar__menue')
    menue__button = logo_bar__menue.find_elements_by_tag_name('a')[0]
    icon_burger = logo_bar__menue.find_element_by_class_name(
        'icon-zon-logo-navigation_menu')

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
    assert logo_bar__menue.is_displayed(), 'Logo bar is not displayed'
    assert menue__button.is_displayed(), 'Menue button is not displayed'
    assert icon_burger.is_displayed(), 'Burger Icon is not displayed'

    menue__button.click()

    # test element states after menue button is clicked
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
    icon_close = logo_bar__menue.find_element_by_class_name(
        'icon-zon-logo-navigation_close-hover')
    assert icon_close.is_displayed(), 'Closing Icon is not displayed'

    menue__button.click()

    # test element states after menue button is clicked again
    assert main_nav__community.is_displayed() is False, (
        'Community bar is displayed')
    assert main_nav__ressorts.is_displayed() is False, (
        'Ressort bar is not displayed')
    assert main_nav__services.is_displayed() is False, (
        'Services bar is not displayed')
    assert main_nav__classifieds.is_displayed() is False, (
        'Classifieds bar is not displayed')
    assert main_nav__search.is_displayed() is False, (
        'Search bar is not displayed')


def test_primary_nav_should_resize_to_fit(
        selenium_driver, testserver):

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

    logo_bar__menue = driver.find_element_by_class_name('logo_bar__menue')
    menu__button = logo_bar__menue.find_elements_by_tag_name('a')[0]
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
    assert (zmo_link.get_attribute('id') ==
            'hp.global.topnav.centerpages.zeitmagazin'), (
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
    view.topic_links = {}
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
