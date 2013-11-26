def test_google_title(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/01' % testserver.url)
    assert driver.title == 'ZMO'
