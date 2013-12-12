import pytest

screen_sizes = ((320, 480, True), (1024, 768, False))


def test_ad_keyword_nofp_nowp(selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(729, 600)
    driver.get('%s/artikel/01' % testserver.url)
    d_sel = "div[data-place='topbanner']"
    d_place = driver.find_element_by_css_selector(d_sel)
    d_ad = d_place.find_element_by_id('iqadtile1')
    d_script = d_ad.find_element_by_tag_name('script')
    d_src = d_script.get_attribute("src")
    assert('noiqdfireplace,noiqdwallpaper' in d_src)


def test_ad_no_keyword(selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(1200, 600)
    driver.get('%s/artikel/01' % testserver.url)
    d_sel = "div[data-place='topbanner']"
    d_place = driver.find_element_by_css_selector(d_sel)
    d_ad = d_place.find_element_by_id('iqadtile1')
    d_script = d_ad.find_element_by_tag_name('script')
    d_src = d_script.get_attribute("src")
    assert('noiqdfireplace,noiqdwallpaper' not in d_src)


@pytest.fixture(scope='session', params=screen_sizes)
def screen_size(request):
    return request.param


def test_ad_display(selenium_driver, testserver, screen_size):
    driver = selenium_driver
    d_sel = "div[data-place='topbanner']"
    m_sel = "div[data-place='mobile_topbanner']"

    # set to small size on first run
    small_screen = screen_size[2]
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/artikel/01' % testserver.url)
    if small_screen:
        m_place = driver.find_element_by_css_selector(m_sel)
        m_ad = m_place.find_element_by_tag_name("div")
        m_class = unicode(m_ad.get_attribute("class"))
        assert('ad__leaderboard--mobile' == m_class)
    else:
        d_place = driver.find_element_by_css_selector(d_sel)
        d_ad = d_place.find_element_by_id('iqadtile1')
        assert(d_ad.is_displayed())
