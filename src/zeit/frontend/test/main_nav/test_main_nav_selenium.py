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
    logo = main_nav.find_element_by_class_name('main-nav__logo__img')
    sharing = main_nav.find_element_by_class_name('main-nav__sharing')
    buttons = sharing.find_elements_by_class_name('main-nav__sharing__item')
    twitter = sharing.find_element_by_class_name('icon-twitter')
    facebook = sharing.find_element_by_class_name('icon-facebook')
    google = sharing.find_element_by_class_name('icon-google')

    # there's exactly one navigation
    assert(len(nav_list) == 1)

    # navigation is visible
    assert(main_nav.is_displayed())

    # there is a logo
    assert(logo.is_displayed())

    # sharing is visible
    assert(sharing.is_displayed())

    # sharing has three buttons
    assert(len(buttons) == 3)

    # twitter, facebook and google buttons are visible
    assert(twitter.is_displayed())
    assert(facebook.is_displayed())
    assert(google.is_displayed())


def test_main_nav(selenium_driver, testserver, screen_size):
    # run twice, once for small screens, once for large
    driver = selenium_driver

    # set to small size on first run
    small_screen = screen_size[2]
    driver.set_window_size(screen_size[0], screen_size[1])

    driver.get('%s/artikel/01' % testserver.url)

    class_trig = "main-nav__section__trigger"
    class_cont = "main-nav__section__content"
    class_input = "main-nav__search__input"
    class_button = "main-nav__search__submit"

    nav_list = driver.find_elements_by_id('js-main-nav')
    main_nav = driver.find_elements_by_id('js-main-nav')[0]
    trigger = main_nav.find_element_by_class_name('main-nav__menu__head')
    menu = main_nav.find_element_by_class_name('main-nav__menu__content')
    logo = main_nav.find_element_by_class_name('main-nav__logo__img')

    res = main_nav.find_element_by_class_name('main-nav__ressorts')
    res_content = res.find_element_by_class_name(class_cont)
    res_links = res_content.find_elements_by_tag_name('a')

    service = main_nav.find_element_by_class_name('main-nav__service')
    service_trig = service.find_element_by_class_name(class_trig)
    service_cont = service.find_element_by_class_name(class_cont)
    service_links = service_cont.find_elements_by_tag_name('a')

    community = main_nav.find_element_by_class_name('main-nav__community')
    community_trig = community.find_element_by_class_name(class_trig)

    search = main_nav.find_element_by_class_name('main-nav__search')
    search_trig = search.find_element_by_class_name(class_trig)
    search_cont = search.find_element_by_class_name(class_cont)
    search_field = search_cont.find_element_by_class_name(class_input)
    search_button = search_cont.find_element_by_class_name(class_button)

    # there's exactly one navigation
    assert(len(nav_list) == 1)

    # navigation is visible
    assert(main_nav.is_displayed())
    assert(trigger.is_displayed())

    # menu is initially hidden on mobile, but visible on desktop
    if small_screen:
        assert(not menu.is_displayed())
    else:
        assert(menu.is_displayed())


    # menu can be opened by click
    if small_screen:
        trigger.click()
    assert(menu.is_displayed())

    # there is a logo
    assert(logo.is_displayed())

    # service is present and can be opened
    assert(service_trig.is_displayed())
    service_trig.click()
    assert(service_cont.is_displayed())

    # service dropdown contains at least one link
    assert(len(service_links) > 0)

    # search is present and can be opened
    assert(search_trig.is_displayed())
    search_trig.click()

    # open search dropdown contains writable input field
    assert(search_field.is_displayed())
    search_string = "Keyword"
    search_field.send_keys(search_string)
    assert(search_field.get_attribute("value") == search_string)

    # open search dropdown contains submit button
    assert(search_button.is_displayed())

    # community is present and can be opened
    assert(community_trig.is_displayed())
    community_trig.click()

    # visible sub res + topics
    assert(res_content.is_displayed())
    assert(len(res_links) > 0)
