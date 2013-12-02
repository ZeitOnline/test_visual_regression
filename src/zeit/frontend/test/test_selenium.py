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
                assert 'figure__video__button' == unicode(
                    but.get_attribute("class"))
            except:
                assert 'figure__video__button icon-playbutton' == unicode(
                    but.get_attribute("class"))
            # after click
            img.click()
            wrap = video.find_element_by_class_name("video__wrapper")
            try:
                wrap.find_element_by_tag_name("object")
            except:
                wrap.find_element_by_tag_name("iframe")
