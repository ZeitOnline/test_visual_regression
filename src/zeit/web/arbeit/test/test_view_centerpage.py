def test_zar_teaser_lead_exists(testbrowser):
    select = testbrowser('/arbeit/centerpage/teaser-lead').cssselect
    assert len(select('.teaser-lead')) == 4


def test_zar_teaser_duo_has_modifier(testbrowser):
    select = testbrowser('/arbeit/centerpage/teaser-duo').cssselect
    assert len(select('.teaser-duo')) == 4
    assert len(select('.teaser-duo--bright')) == 2
    assert len(select('.teaser-duo--dark')) == 2


def test_zar_jobbox_dropdown_has_correct_structure(testbrowser):
    select = testbrowser('/arbeit/centerpage/jobbox-dropdown').cssselect
    assert len(select('.jobbox-dropdown')) == 2
    assert len(select('.jobbox-dropdown__label')) == 2
    assert len(select('.jobbox-dropdown__dropdown')) == 2
    assert len(select('.jobbox-dropdown__button')) == 2


def test_zar_jobbox_dropdown_changes_link_on_select(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/arbeit/centerpage/jobbox-dropdown' % testserver.url)
    dropdown = driver.find_element_by_class_name('jobbox-dropdown__dropdown')
    dropdown.find_element_by_xpath("//option[text()='Kunst & Kultur']").click()

    button = driver.find_element_by_class_name('jobbox-dropdown__button')
    button_url = button.get_attribute('href')
    assert 'stellenmarkt/kultur_kunst' in button_url
    assert 'stellenmarkt.funktionsbox.streifen' in button_url
