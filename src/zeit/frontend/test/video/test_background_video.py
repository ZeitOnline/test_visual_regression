def test_background_video_html(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/06' % testserver.url)
    cssclass = 'article__main-video--longform'
    for video in driver.find_elements_by_class_name(cssclass):
        source = video.find_element_by_tag_name("source")
        fallback = video.find_element_by_tag_name("div")
        assert 'video/mp4' == unicode(source.get_attribute("type"))
        assert 'article__main-image--longform video--fallback' == unicode(
            fallback.get_attribute("class"))
