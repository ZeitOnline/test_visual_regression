import pytest

def test_ad_keyword_diuqilon(selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(768, 1024)
    driver.get('%s/artikel/01' % testserver.url)
    diuqilon = driver.execute_script("return window.diuqilon")
    height = driver.execute_script("return screen.height")
    width = driver.execute_script("return window.innerWidth")
    print height
    print width
    # ipad
    assert diuqilon == ',diuqilon'
    driver.set_window_size(1024, 768)
    driver.get('%s/artikel/01' % testserver.url)
    diuqilon = driver.execute_script("return window.diuqilon")
    # not ipad
    assert diuqilon == ''


def test_ad_display(selenium_driver, testserver):
    driver = selenium_driver
    m_sel = "div[id='sas_13500']"
    driver.set_window_size(320, 480)
    driver.get('%s/artikel/01' % testserver.url)
    assert driver.find_element_by_css_selector(m_sel) != 0


def test_viewport_resizer(selenium_driver, testserver):
    driver = selenium_driver
    m_sel = "meta[id='viewport-meta']"
    # ipad landscape
    driver.set_window_size(1024, 768)
    driver.get('%s/artikel/01' % testserver.url)
    content = driver.execute_script("return document.getElementById('viewport-meta').getAttribute('content')")
    assert 'width=1280' in content
    # ipad portrait and smaller
    # doesn't work in ff
    if('firefox' not in driver.name):
        driver.set_window_size(768, 1024)
        driver.get('%s/artikel/01' % testserver.url)
        content = driver.execute_script("return document.getElementById('viewport-meta').getAttribute('content')")
        assert 'width=device-width' in content
    else:
        print 'test passed because of browser/driver incompatiblilty'


