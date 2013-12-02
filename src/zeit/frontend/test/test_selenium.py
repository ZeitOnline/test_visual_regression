def test_video_html(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/01' % testserver.url)
    for video in driver.find_elements_by_tag_name('figure'):
        if video.get_attribute("data-video"):
            still = video.find_element_by_tag_name("div")
            img = video.find_element_by_tag_name("img")
            but = video.find_element_by_tag_name("span")
            cap = video.find_element_by_tag_name("figcaption")
            assert 'video__still' == unicode(still.get_attribute("class"))
            assert 'figure__media' == unicode(img.get_attribute("class"))
            assert 'true' == unicode(but.get_attribute("data-video-button"))
            assert 'figure__caption' == unicode(cap.get_attribute("class"))
            img.click()
            wrap = video.find_element_by_class_name("video__wrapper")
            try:
                wrap.find_element_by_tag_name("object")
            except:
                wrap.find_element_by_tag_name("iframe")
