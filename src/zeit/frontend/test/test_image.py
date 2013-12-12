

def test_image_download(browser, asset):
    path = '/politik/deutschland/2013-07/bnd/bnd-148x84.jpg'
    result = browser.get(path)
    assert ''.join(result.app_iter) == asset(path).read()
    assert result.headers['Content-Length'] == '4843'
    assert result.headers['Content-Type'] == 'image/jpeg; charset=UTF-8'
    assert result.headers['Content-Disposition'] == 'inline; filename="bnd-148x84.jpg"'
