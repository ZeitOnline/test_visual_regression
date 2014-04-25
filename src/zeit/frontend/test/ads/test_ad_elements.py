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


def test_viewport_is_resized_in_ipad_landscape(selenium_driver, testserver):
    driver = selenium_driver
    m_sel = "meta[id='viewport-meta']"
    driver.set_window_size(1024, 768)
    driver.get('%s/artikel/01' % testserver.url)
    content = driver.execute_script("return document.getElementById('viewport-meta').getAttribute('content')")
    orientation = driver.execute_script("return Math.abs(window.orientation)")
    if(orientation is 90):
        # ipad landscape
        assert 'width=1280' in content


def test_viewport_is_not_resized_in_other_browser(selenium_driver, testserver):
    driver = selenium_driver
    m_sel = "meta[id='viewport-meta']"
    driver.set_window_size(1024, 768)
    driver.get('%s/artikel/01' % testserver.url)
    content = driver.execute_script("return document.getElementById('viewport-meta').getAttribute('content')")
    orientation = driver.execute_script("return Math.abs(window.orientation)")
    if(orientation is not 90):
        # all other
        assert 'width=device-width' in content


def test_var_IQD_varPack_isset(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/01' % testserver.url)
    varpack = driver.execute_script("return typeof window.IQD_varPack");
    assert varpack == "object"


def test_var_Krux_isset(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/01' % testserver.url)
    krux = driver.execute_script("return typeof window.Krux");
    assert krux == "function"
