from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zope.testbrowser.browser import Browser


def test_inline_gallery_is_there(testserver):
    browser = Browser('%s/artikel/01' % testserver.url)
    assert '<div class="inline-gallery"' in browser.contents


def test_inline_gallery_buttons(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/01' % testserver.url)
    try:
        cond = EC.presence_of_element_located((By.CLASS_NAME, "bx-wrapper"))
        WebDriverWait(driver, 10).until(cond)
        nextselector = ".bx-next"
        prevselector = ".bx-prev"
        onextselector = ".bx-overlay-next"
        # test navigation buttons
        nextbutton = driver.find_element_by_css_selector(nextselector)
        prevbutton = driver.find_element_by_css_selector(prevselector)
        assert nextbutton
        assert prevbutton
        nextbutton.click()
        prevbutton.click()
        # test overlay buttons
        overlaynext = driver.find_element_by_css_selector(onextselector)
        script = 'return $(".bx-overlay-next").css("opacity")'
        elemOpacity = driver.execute_script(script)
        overlayprev = driver.find_element_by_css_selector(onextselector)
        assert overlaynext
        assert overlayprev
        overlaynext.click()
        script = 'return $(".bx-overlay-next").css("opacity")'
        elemOpacityLater = driver.execute_script(script)
        overlayprev.click()
        # opacity should have changed
        assert elemOpacity != elemOpacityLater
    except:
        print "Timeout Gallery Script"
        assert False
