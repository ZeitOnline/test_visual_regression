# -*- coding: utf-8 -*-
import pytest

screen_sizes = ((320, 480, True), (1024, 768, False))


@pytest.fixture(scope='session', params=screen_sizes)
def screen_size(request):
    return request.param


def test_compact_main_nav(selenium_driver, testserver, screen_size):
    # run twice, once for small screens, once for large
    driver = selenium_driver

    # set to small size on first run
    small_screen = screen_size[2]
    driver.set_window_size(screen_size[0], screen_size[1])

    driver.get('%s/artikel/05' % testserver.url)

    nav_list = driver.find_elements_by_class_name('main-nav')
    main_nav = driver.find_elements_by_class_name('main-nav')[0]
    logo_small = main_nav.find_element_by_css_selector(
        '.main-nav__brand-logo--small')
    logo_large = main_nav.find_element_by_css_selector(
        '.main-nav__brand-logo--large')
    sharing = main_nav.find_element_by_class_name('main-nav__sharing')
    buttons = sharing.find_elements_by_class_name('main-nav__sharing__item')
    icons = sharing.find_elements_by_class_name('main-nav__sharing-icon')

    # there's exactly one navigation
    assert len(nav_list) == 1

    # navigation is visible
    assert main_nav.is_displayed()

    # there is the right logo visible
    if small_screen:
        assert logo_small.is_displayed()
        assert not logo_large.is_displayed()
    else:
        assert not logo_small.is_displayed()
        assert logo_large.is_displayed()

    # sharing is visible
    assert sharing.is_displayed()

    # sharing has three buttons
    assert len(buttons) == 3

    # twitter, facebook and google buttons are visible
    for icon in icons:
        assert icon.is_displayed()


def test_main_nav(selenium_driver, testserver, screen_size):
    # run twice, once for small screens, once for large
    driver = selenium_driver

    # set to small size on first run
    small_screen = screen_size[2]
    driver.set_window_size(screen_size[0], screen_size[1])

    driver.get('%s/artikel/01' % testserver.url)

    class_trig = "main-nav__section__trigger"
    class_cont = "main-nav__section__content"

    nav_list = driver.find_elements_by_id('js-main-nav')
    main_nav = driver.find_element_by_id('js-main-nav')
    trigger = driver.find_element_by_id('js-main-nav-trigger')
    menu = main_nav.find_element_by_class_name('main-nav__menu__content')
    logo_small = main_nav.find_element_by_css_selector(
        '.main-nav__brand-logo--small')
    logo_large = main_nav.find_element_by_css_selector(
        '.main-nav__brand-logo--large')

    res = main_nav.find_element_by_class_name('main-nav__ressorts')
    res_content = res.find_element_by_class_name('main-nav__ressort-list')
    res_links = res_content.find_elements_by_tag_name('a')

    service = main_nav.find_element_by_class_name('main-nav__service')
    service_trig = service.find_element_by_class_name(class_trig)
    service_cont = service.find_element_by_class_name(class_cont)
    service_links = service_cont.find_elements_by_tag_name('a')

    # community = main_nav.find_element_by_class_name('main-nav__community')
    # community_trig = community.find_element_by_class_name(class_trig)

    # there's exactly one navigation
    assert len(nav_list) == 1

    # navigation is visible
    assert main_nav.is_displayed()

    # menu is initially hidden on mobile, but visible on desktop
    if small_screen:
        assert trigger.is_displayed()
        assert not menu.is_displayed()
    else:
        assert not trigger.is_displayed()
        assert menu.is_displayed()

    # menu can be opened by click
    if small_screen:
        trigger.click()
    assert menu.is_displayed()

    # there is the right logo visible
    if small_screen:
        assert logo_small.is_displayed()
        assert not logo_large.is_displayed()
    else:
        assert not logo_small.is_displayed()
        assert logo_large.is_displayed()

    # service is present and can be opened
    assert service_trig.is_displayed()
    service_trig.click()
    assert service_cont.is_displayed()

    # service dropdown contains at least one link
    assert len(service_links) > 0

    # visible sub res + topics
    assert res_content.is_displayed()
    assert len(res_links) > 0
