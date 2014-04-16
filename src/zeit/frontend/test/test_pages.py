def test_js_flawless_document_load(selenium_driver, testserver):
    driver = selenium_driver
    for i in range(1, 10):
        driver.get('%s/artikel/%02d' % (testserver.url, i))
        errors = driver.execute_script('return window.jsErrors');
        assert not errors
