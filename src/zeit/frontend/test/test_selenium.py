def test_video_html(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/01' % testserver.url)
    for video in driver.find_elements_by_tag_name('figure'):
        if video.get_attribute("data-video"):
            still = video.find_element_by_tag_name("div")
            img = video.find_element_by_tag_name("img")
            but = video.find_element_by_tag_name("span")
            cap = video.find_element_by_tag_name("figcaption")
            # before click
            assert 'video__still' == unicode(still.get_attribute("class"))
            assert 'figure__media' == unicode(img.get_attribute("class"))
            assert 'figure__caption' == unicode(cap.get_attribute("class"))
            try:
                assert 'video__button' == unicode(
                    but.get_attribute("class"))
            except:
                assert 'video__button icon-playbutton' == unicode(
                    but.get_attribute("class"))
            # after click
            img.click()
            wrap = video.find_element_by_class_name("video__wrapper")
            try:
                wrap.find_element_by_tag_name("object")
            except:
                wrap.find_element_by_tag_name("iframe")
            # test if the correct video is shown
            assert wrap.get_attribute(
                "data-video") == video.get_attribute("data-video")


def test_main_nav(selenium_driver, testserver):
    # run twice, once for small screens, once for large
    for x in range(0, 2):
        driver = selenium_driver

        if x == 0:
            # set to small size on first run
            small_screen = True
            driver.set_window_size(320, 480)
        else:
            # set to full size on second run
            driver.set_window_size(1024, 768)
            small_screen = False

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

        all_res = main_nav.find_element_by_class_name('main-nav__all-ressorts')
        all_res_trig = all_res.find_element_by_class_name(class_trig)
        all_res_cont = all_res.find_element_by_class_name(class_cont)
        all_res_links = all_res_cont.find_elements_by_tag_name('a')

        res = main_nav.find_element_by_class_name('main-nav__ressorts')
        res_content = res.find_element_by_class_name(class_cont)
        res_links = res_content.find_elements_by_tag_name('a')

        service = main_nav.find_element_by_class_name('main-nav__service')
        service_trig = service.find_element_by_class_name(class_trig)
        service_cont = service.find_element_by_class_name(class_cont)
        service_links = service_cont.find_elements_by_tag_name('a')

        community = main_nav.find_element_by_class_name('main-nav__community')
        community_trig = community.find_element_by_class_name(class_trig)
        community_cont = community.find_element_by_class_name(class_cont)
        community_links = community_cont.find_elements_by_tag_name('a')

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
        trigger.click()
        assert(menu.is_displayed())

        # there is a logo
        assert(logo.is_displayed())

        # all res are present and can be opened
        assert(all_res_trig.is_displayed())
        all_res_trig.click()
        assert(all_res_cont.is_displayed())

        # all res dropdown contains at least one link
        assert(len(all_res_links) > 0)

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
        assert(community_cont.is_displayed())

        # community dropdown contains at least one link
        assert(len(community_links) > 0)

        # visible sub res + topics
        assert(res_content.is_displayed())
        assert(len(res_links) > 0)
