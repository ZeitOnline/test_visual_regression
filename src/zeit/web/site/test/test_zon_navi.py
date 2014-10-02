# -*- coding: utf-8 -*-
import lxml
import pytest


def test_nav_markup_should_match_css_selectors(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/nav_main.html')
    html_str = tpl.render()
    html = lxml.html.fromstring(html_str).cssselect
    assert len(html('nav.main_nav')) == 1, (
        'just one .main_nav should be present')

    assert len(html('nav.main_nav > div')) == 9, (
        'nine divs within .main_nav')

    assert '</div><div class="main_nav__date"' in html_str, (
        'don\'t break line here, due to inline-block state')

    assert len(html('nav.main_nav > div.logo_bar >'
                    'div.logo_bar__image')) == 1, 'just one .logo_bar__image'

    assert len(html('nav.main_nav > div.logo_bar >'
                    'div.logo_bar__menue')) == 1, 'just one .logo_bar__menue'

    assert len(html('nav.main_nav > div.main_nav__teaser')) == 1, (
        'just one .main_nav__teaser')

    assert len(html('nav.main_nav > div.main_nav__community'
                    '[data-dropdown="true"]')) == 1, (
        'just one .main_nav__community w/ data-dropdown=true')

    assert len(html('nav.main_nav > div.main_nav__ressorts'
                    '[data-dropdown="true"]')) == 1, (
        'just one .main_nav__ressorts w/ data-dropdown=true')

    assert len(html('nav.main_nav > div.main_nav__services'
                    '[data-dropdown="true"]')) == 1, (
        'just one .main_nav__services w/ data-dropdown=true')

    assert len(html('nav.main_nav > div.main_nav__classifieds'
                    '[data-dropdown="true"]')) == 1, (
        'just one .main_nav__classifieds w/ data-dropdown=true')

    assert len(html('nav.main_nav > div.main_nav__search'
                    '[data-dropdown="true"]')) == 1, (
        'just one .main_nav__search w/ data-dropdown=true')

    assert len(html('nav.main_nav > div.main_nav__tags')) == 1, (
        'just one .main_nav__tags')

    assert len(html('nav.main_nav > div.main_nav__date')) == 1, (
        'just one .main_nav__date')


def test_nav_services_macro_should_have_expected_links(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/nav_main.html')
    html_str = tpl.module.main_nav_services()
    html = lxml.html.fromstring(html_str).cssselect
    assert html('li > a[href="http://www.zeitabo.de/'
                '?mcwt=2009_07_0002"]')[0] is not None, (
        'No link for zeitabo.de')
    assert html('li > a[href="http://shop.zeit.de?et=l6VVNm&et_cid=42&'
                'et_lid=175&et_sub=Startseite_header"]'
                '[id="hp.global.topnav.links.shop"]')[0] is not None, (
        'No link for shop.zeit.de')
    assert html('li > a[href="https://premium.zeit.de/?wt_mc=pm.intern.fix.'
                'zeitde.fix.dach.text.epaper"]'
                '[id="hp.global.topnav.links.epaper"]')[0] is not None, (
        'No link for premium.zeit.de')
    assert html('li > a[href="https://premium.zeit.de/abo/digitalpaket5'
                '?wt_mc=pm.intern.fix.zeitde.fix.dach.text.audio"]'
                '[id="hp.global.'
                'topnav.links.audio"]')[0] is not None, (
        'No link for premium.zeit.de AUDIO')
    assert html('li > a[href="https://premium.zeit.de/abo/appsios?'
                'wt_mc=pm.intern.fix.zeitde.fix.dach.text.apps"]'
                '[id="hp.global.topnav'
                '.links.apps"]')[0] is not None, (
        'No link for premium.zeit.de APPS')
    assert html('li > a[href="http://www.zeit.de/archiv"][id="hp.global.'
                'topnav.links.archiv"]')[0] is not None, 'No link for Archiv'


def test_nav_classifieds_macro_should_have_expected_structure(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/nav_main.html')
    html_str = tpl.module.main_nav_classifieds()
    html = lxml.html.fromstring(html_str).cssselect
    assert html('li > a[href="http://jobs.zeit.de/"]'
                '[id="hp.global.topnav.links.jobs"]')[0] is not None, (
        'No link for job.zeit.de')
    assert html('li > a[href="http://www.zeit.de/angebote/partnersuche/index?'
                'pscode=01_100_20003_0001_0001_0005_empty_AF00ID_GV00ID"]'
                '[id="hp.global.topnav.links.partnersuche"]')[0] is not None, (
        'Link for partnersuche not present')
    assert len(html('li.main_nav__classifieds__more')) == 1, 'No classifieds'
    assert html('li > a[href="http://zeit.immowelt.de/"]'
                '[id="hp.global.topnav.links.immobilien"]'
                '[rel="nofollow"]')[0] is not None, (
        'No link for zeit.immowelt.de')
    assert html('li > a[href="http://automarkt.zeit.de/"]'
                '[id="hp.global.topnav.links.automarkt"]')[0] is not None, (
        'No link for Automarkt')


def test_nav_community_macro_should_render_a_login(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/nav_main.html')
    html_str = tpl.module.main_nav_community()
    html = lxml.html.fromstring(html_str).cssselect
    print html_str
    assert html('a[href="http://community.zeit.de/user/login?destination='
                'http://www.zeit.de/index"]'
                '[rel="nofollow"]'
                '[class="user"]'
                '[id="drupal_login"]')[0] is not None, (
        'Community login is missing')


def test_nav_main_nav_logo_should_create_a_logo_link(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/nav_main.html')
    html_str = tpl.module.main_nav_logo()
    html = lxml.html.fromstring(html_str).cssselect
    assert html('a[href="http://www.zeit.de/index"]'
                '[title="Nachrichten auf ZEIT ONLINE"]'
                '[class="icon-zon-logo-desktop"]'
                '[id="hp.global.topnav.centerpages.logo"]')[0] is not None, (
        'Logo link is missing')


def test_nav_main_nav_burger_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/nav_main.html')
    html_str = tpl.module.main_nav_burger()
    html = lxml.html.fromstring(html_str).cssselect
    print html_str
    assert html('a')[0] is not None, 'An empty link is not present'
    assert len(html('div.logo_bar__menue__image.main_nav__icon--plain'
                    '.icon-zon-logo-navigation_menu')) == 1, (
        'Logo for bar menu is not present')
    assert len(html('div.logo_bar__menue__image'
                    '.main_nav__icon--hover.icon-zon-logo-'
                    'navigation_menu-hover')) == 1, (
        "A div for the burger menu is missing.")


def test_nav_macro_main_nav_search_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/nav_main.html')
    html_str = tpl.module.main_nav_search()
    html = lxml.html.fromstring(html_str).cssselect

    assert html('form.search'
                '[accept-charset="utf-8"]'
                '[method="get"]'
                '[role="search"]'
                '[action="http://www.zeit.de/suche/index"]')[0] is not None, (
        'Form element is not present')
    assert html('label.hideme[for="q"]')[0] is not None, (
        'Hide me label is not present')
    assert html('button.search__button[type="submit"]'
                '[tabindex="2"]')[0] is not None, 'No search button present'
    assert html('span.icon-zon-logo-navigation_suche'
                '.search__button__image.'
                'main_nav__icon--plain')[0] is not None, (
        'No search logo present')
    assert html('span.icon-zon-logo-navigation_suche-hover'
                '.search__button__image.'
                'main_nav__icon--hover')[0] is not None, (
        'No icon-hover present')
    assert html('input.search__input[id="q"][name="q"]'
                '[type="search"][placeholder="Suche"]'
                '[tabindex="1"]')[0] is not None, (
        'No search input present')


def test_macro_main_nav_ressorts_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/nav_main.html')
    html_str = tpl.module.main_nav_ressorts()
    html = lxml.html.fromstring(html_str).cssselect

    assert len(html('nav[role="navigation"] ul.primary-nav')) == 1
    assert len(html('ul li.primary-nav__item')) > 1
    assert len(html('ul li.primary-nav__item a.primary-nav__link')) == (
        len(html('ul li.primary-nav__item'))), (
        'Links must have same length a list items.')


def test_macro_main_nav_tags_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/nav_main.html')
    html_str = tpl.module.main_nav_tags()
    html = lxml.html.fromstring(html_str).cssselect
    assert html('span.main_nav__tags__label')[0] is not None, (
        'Label span is not present')
    assert html('ul')[0] is not None, 'A list for the tags is not present.'


def test_macro_main_nav_date_should_return_what_was_given(jinja2_env):
    # ToDo: Maybe fill this function with more sense?
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/nav_main.html')
    html_str = tpl.module.main_nav_date('Mein Datum')
    assert html_str == 'Mein Datum'


# integration testing

def test_article_should_have_valid_main_nav_structure(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    html = browser.cssselect
    print browser.contents
    assert len(html('nav.main_nav')) == 1, 'Nav main_nav is not present.'
    assert len(html('div.logo_bar__image')) == 1, 'Logo bar image not present.'
    assert len(html('div.logo_bar__menue')) == 1, 'Menu bar is not present.'
    assert len(html('div.main_nav__teaser')) == 1, 'Nav teaser not present.'
    assert len(html('div.main_nav__community[data-dropdown="true"]')) == 1, (
        'Data dropdown not present')


def test_article_should_have_valid_services_structure(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    html = browser.cssselect
    print browser.contents
    assert len(html('a[id="hp.global.topnav.links.abo"]')) == 1, (
        'Abo link not present.')
    assert len(html('a[id="hp.global.topnav.links.shop"]')) == 1, (
        'Shop link is not present')
    assert len(html('a[id="hp.global.topnav.links.epaper"]')) == 1, (
        'E-Paper link is not present.')
    assert len(html('a[id="hp.global.topnav.links.audio"]')) == 1, (
        'Audio link is not present.')
    assert len(html('a[id="hp.global.topnav.links.apps"]')) == 1, (
        'App link is not present.')
    assert len(html('a[id="hp.global.topnav.links.archiv"]')) == 1, (
        'Archiv link is not present')


def test_article_should_have_valid_classifieds_structure(testserver,
                                                         testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    html = browser.cssselect
    print browser.contents
    assert len(html('a[id="hp.global.topnav.links.jobs"]')) == 1, (
        'Job link is not present.')
    assert len(html('a[id="hp.global.topnav.links.partnersuche"]')) == 1, (
        'Link partnersuche is not present.')
    assert len(html('a[id="hp.global.topnav.links.immobilien"]')) == 1, (
        'Link immobilien is not present')
    assert len(html('a[id="hp.global.topnav.links.automarkt"]')) == 1, (
        'Link automarkt is not present')


def test_article_has_valid_community_structure(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    html_str = browser.contents
    html = lxml.html.fromstring(html_str).cssselect
    assert html(
        'a[href="http://community.zeit.de/user/login?"]') is not None, (
        'Link to login form is invalid')
    assert html('span.main_nav__community__image') is not None, (
        'span.main_nav__community__image is invalid')
    assert 'Anmelden' in lxml.etree.tostring(
        html('a[id="drupal_login"]')[0]), (
        'Link to login has invalid label')


def test_article_has_valid_logo_structure(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    html_str = browser.contents
    html = lxml.html.fromstring(html_str).cssselect
    assert html('a.icon-zon-logo-desktop'
                '[href="http://www.zeit.de/index"]'
                '[title="Nachrichten auf ZEIT ONLINE"]'
                '[id="hp.global.topnav.centerpages.logo"]') is not None, (
        'Element a.icon-zon-logo-desktop is invalid')


def test_article_has_valid_burger_structure(testserver, testbrowser):
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


def test_article_has_valid_search_structure(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    html_str = browser.contents
    html = lxml.html.fromstring(html_str).cssselect
    assert html('form.search'
                '[accept-charset="utf-8"]'
                '[method="get"]'
                '[role="search"]'
                '[action="http://www.zeit.de/suche/index"]') is not None, (
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


def test_article_has_valid_tag_structure(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    html_str = browser.contents
    html = lxml.html.fromstring(html_str).cssselect
    assert 'Schwerpunkte' in html('span.main_nav__tags__label')[0].text, (
        'Element main_nav__tags__label is invalid')
    assert html('ul'), 'Missing ul'


def test_article_has_valid_nav_date_structure(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    date = '3. September 2014 10:50 Uhr'
    html_str = browser.contents
    html = lxml.html.fromstring(html_str).cssselect
    assert html('div.main_nav__date')[0].text == date, (
        'Date is invalid')

# selenium test

screen_sizes = ((320, 480, True), (520, 960, True),
                (768, 1024, False), (980, 1024, False))


@pytest.fixture(scope='session', params=screen_sizes)
def screen_size(request):
    return request.param


def test_zon_main_nav_has_correct_structure(
        selenium_driver, testserver, screen_size):

    driver = selenium_driver
    small_screen = screen_size[2]
    screen_width = screen_size[0]
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/centerpage/zeitonline' % testserver.url)

    main_nav = driver.find_elements_by_class_name('main_nav')[0]
    logo_bar__image = driver.find_elements_by_class_name('logo_bar__image')[0]
    search__button = driver.find_elements_by_class_name('search__button')[0]
    search__input = driver.find_elements_by_class_name('search__input')[0]
    main_nav__community = driver.find_elements_by_class_name(
        'main_nav__community')[0]
    logo_bar__menue = driver.find_elements_by_class_name('logo_bar__menue')[0]
    main_nav__tags = driver.find_elements_by_class_name('main_nav__tags')[0]
    main_nav__ressorts = driver.find_elements_by_class_name(
        'main_nav__ressorts')[0]
    main_nav__date = driver.find_elements_by_class_name('main_nav__date')[0]
    main_nav__services = driver.find_elements_by_class_name(
        'main_nav__services')[0]
    main_nav__classifieds = driver.find_elements_by_class_name(
        'main_nav__classifieds')[0]

    # navigation is visible in all sizes
    assert(main_nav.is_displayed())
    # logo is visible in all sizes
    assert(logo_bar__image.is_displayed())

    if small_screen:
        # burger menue is visible
        assert(logo_bar__menue.is_displayed())
        # tags are hidden
        assert(main_nav__tags.is_displayed() is False)
        # date bar is hidden
        assert(main_nav__date.is_displayed() is False)
        # last 3 services aren't shown
        serv_li = main_nav__services.find_elements_by_tag_name('li')
        assert(serv_li[3].is_displayed() is False)
        assert(serv_li[4].is_displayed() is False)
        assert(serv_li[5].is_displayed() is False)
    else:
        # search button is visible in desktop mode
        assert(search__button.is_displayed())
        # community link is visible in desktop mode
        assert(main_nav__community.is_displayed())
        # ressort bar is visible in desktop mode
        assert(main_nav__ressorts.is_displayed())
        # service bar is visible in desktop mode
        assert(main_nav__services.is_displayed())
        # classifieds bar is visible in desktop mode
        assert(main_nav__classifieds.is_displayed())

    if screen_width == 768:
        # test search input is hidden in tablet mode
        assert(search__input.is_displayed() is False)


def test_nav_search_is_working_as_expected(
        selenium_driver, testserver, screen_size):

    driver = selenium_driver
    small_screen = screen_size[2]
    screen_width = screen_size[0]
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/centerpage/zeitonline' % testserver.url)

    search__button = driver.find_elements_by_class_name('search__button')[0]
    search__input = driver.find_elements_by_class_name('search__input')[0]
    logo_bar__menue = driver.find_element_by_class_name('logo_bar__menue')
    menu__button = logo_bar__menue.find_elements_by_tag_name('a')[0]
    document = driver.find_element_by_class_name('page')

    if screen_width == 768:
        # test search input is shown after button click
        search__button.click()
        assert(search__input.is_displayed()), 'Input is not displayed'
        # test search input is not hidden after click in input
        search__input.click()
        assert(search__input.is_displayed()), 'Input is not displayed'
        # test search input is hidden after button click, if its empty
        search__button.click()
        assert(search__input.is_displayed() is False), 'Input is displayed'
        # test search input is hidden after click somewhere else
        document.click()
        assert(search__input.is_displayed() is False), 'Input is displayed'
        search__button.click()

    # open search for mobile
    if screen_width < 768:
        menu__button.click()

    # test if search is performed
    search__input.send_keys("test")
    search__button.click()

    assert driver.current_url == 'http://www.zeit.de/suche/index?q=test', (
        'Search wasnt performed')


def test_nav_burger_menue_is_working_as_expected(
        selenium_driver, testserver):

    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/centerpage/zeitonline' % testserver.url)

    logo_bar__menue = driver.find_element_by_class_name('logo_bar__menue')
    menu__button = logo_bar__menue.find_elements_by_tag_name('a')[0]
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
    assert(logo_bar__menue.is_displayed()), 'Logo bar is not displayed'
    assert(menu__button.is_displayed()), 'Menue button is not displayed'
    assert(icon_burger.is_displayed()), 'Burger Icon is not displayed'

    menu__button.click()

    # test element states after menue button is clicked
    assert(main_nav__community.is_displayed()), (
        'Community bar is not displayed')
    assert(main_nav__ressorts.is_displayed()), (
        'Ressort bar is not displayed')
    assert(main_nav__services.is_displayed()), (
        'Services bar is not displayed')
    assert(main_nav__classifieds.is_displayed()), (
        'Classifieds bar is not displayed')
    assert(main_nav__search.is_displayed()), (
        'Search bar is not displayed')

    # test close button is displayed
    icon_close = logo_bar__menue.find_element_by_class_name(
        'icon-zon-logo-navigation_close-hover')
    assert(icon_close.is_displayed()), 'Closing Icon is not displayed'

    menu__button.click()

    # test element states after menue button is clicked again
    assert(main_nav__community.is_displayed() is False), (
        'Community bar is displayed')
    assert(main_nav__ressorts.is_displayed() is False), (
        'Ressort bar is not displayed')
    assert(main_nav__services.is_displayed() is False), (
        'Services bar is not displayed')
    assert(main_nav__classifieds.is_displayed() is False), (
        'Classifieds bar is not displayed')
    assert(main_nav__search.is_displayed() is False), (
        'Search bar is not displayed')
