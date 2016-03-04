from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

import zeit.cms.interfaces

import zeit.web.core.interfaces


def test_campus_centerpage_should_produce_regular_topiclinks(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/centerpage/index')
    topiclink = zeit.web.core.interfaces.ITopicLink(context)
    labels = sorted(dict(topiclink).keys())
    assert labels == ['Ausdauersport', 'Bayerische Landesbank', 'Paul Auster']


def test_campus_article_should_import_topiclinks(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/simple')
    topiclink = zeit.web.core.interfaces.ITopicLink(context)
    labels = sorted(dict(topiclink).keys())
    assert labels == ['Ausdauersport', 'Bayerische Landesbank', 'Paul Auster']


def test_campus_article_should_use_default_topiclinks_of_hp(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/simple')
    article_topiclink = zeit.web.core.interfaces.ITopicLink(context)

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/index')
    hp_topiclink = zeit.web.core.interfaces.ITopicLink(context)

    assert article_topiclink == hp_topiclink


def test_campus_navigation_should_present_flyout(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/campus/index' % testserver.url)
    link = driver.find_element_by_css_selector(
        '.nav__tools-title .nav__dropdown')
    link.click()
    try:
        WebDriverWait(driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, 'nav-flyout')))
    except TimeoutException:
        assert False, 'Navigation flyout not visible within 5 seconds'
    else:
        flyout = driver.find_elements_by_css_selector(
            '.nav-flyout__item')
        assert len(flyout) == 3
        link.click()
        try:
            WebDriverWait(driver, 5).until(
                expected_conditions.invisibility_of_element_located(
                    (By.CLASS_NAME, 'nav-flyout')))
        except TimeoutException:
            assert False, 'Navigation flyout not hidden within 5 seconds'
        else:
            assert True
