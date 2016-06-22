# -*- coding: utf-8 -*-


def test_background_video_html(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/article/06' % testserver.url)
    cssclass = 'article__main-video--longform'
    for video in driver.find_elements_by_class_name(cssclass):
        fallback = video.find_element_by_tag_name("img")
        video.find_element_by_xpath("//source[@type='video/mp4']")
        video.find_element_by_xpath("//source[@type='video/webm']")
        assert 'video--fallback ' == unicode(fallback.get_attribute("class"))
