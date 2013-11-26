def test_google_title(selenium_driver):
    driver = selenium_driver
    driver.get("http://localhost:9090/artikel/01")
    assert "ZMO" in driver.title
