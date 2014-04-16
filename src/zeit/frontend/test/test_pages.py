def test_js_flawless_document_load(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/07' % testserver.url)
    errors = driver.execute_script('return window.jsErrors');
    assert not errors
