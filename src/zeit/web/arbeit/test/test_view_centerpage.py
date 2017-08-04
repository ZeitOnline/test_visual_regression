def test_zar_teaser_lead_has_correct_structure(testbrowser):
    select = testbrowser('/arbeit/centerpage/teaser-lead').cssselect
    assert len(select('.teaser-lead')) == 4

    # byline only if it exists
    assert len(select('.teaser-lead__byline')) == 3

    # show fallback image if no image exists
    assert 1 == len(select(
        '.teaser-lead__media img[src*="/zeit-magazin/default/teaser_image/"]'))


def test_zar_teaser_duo_has_modifier(testbrowser):
    select = testbrowser('/arbeit/centerpage/teaser-duo').cssselect
    assert len(select('.teaser-duo')) == 4
    assert len(select('.teaser-duo--bright')) == 2
    assert len(select('.teaser-duo--dark')) == 2


def test_zar_teaser_small_has_correct_structure(testbrowser):
    select = testbrowser('/arbeit/centerpage/teaser-small').cssselect
    assert len(select('.teaser-small')) == 6
    assert len(select('.teaser-small__kicker')) == 6
    assert len(select('.teaser-small__title')) == 6
    assert len(select('.teaser-small__byline')) == 5
    assert len(select('.series-label')) == 2
    # Fallback image if article/teaser has none
    assert 2 == len(select(
        '.teaser-small img[src*="/zeit-magazin/default/teaser_image/"]'))


def test_zar_teaser_small_should_display_no_image_on_mobile(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/arbeit/centerpage/teaser-small' % testserver.url)
    teaser_images = driver.find_elements_by_class_name('teaser-small__media')
    assert len(teaser_images) == 6
    for teaser_image in teaser_images:
        assert teaser_image.is_displayed() is False


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


def test_zar_teaser_topic_has_correct_structure(testbrowser):
    select = testbrowser('/arbeit/centerpage/teaser-topic').cssselect
    assert len(select('.teaser-topic')) == 1
    assert len(select('.teaser-topic-main')) == 1
    assert len(select('.teaser-topic-sub')) == 3

    assert len(select('.teaser-topic-main__button[href*="/thema/"]')) == 1

    # Fallback image if article/teaser has none
    assert 1 == len(select(
        '.teaser-topic img[src*="/zeit-magazin/default/teaser_image/"]'))


def test_zar_steaser_topic_should_display_no_image_on_mobile(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/arbeit/centerpage/teaser-topic' % testserver.url)
    teaser_images = driver.find_elements_by_class_name(
        'teaser-topic-sub__media')
    assert len(teaser_images) == 3
    for teaser_image in teaser_images:
        assert teaser_image.is_displayed() is False
