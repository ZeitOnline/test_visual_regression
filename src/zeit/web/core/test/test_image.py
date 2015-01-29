# -*- coding: utf-8 -*-
from hashlib import sha1
from StringIO import StringIO

from PIL import Image

import zeit.cms.interfaces


def test_image_download(appbrowser):
    path = '/politik/deutschland/2013-07/bnd/bnd-148x84.jpg'
    result = appbrowser.get(path)
    image = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/' + path)
    assert ''.join(result.app_iter) == image.open().read()
    assert result.headers['Content-Length'] == '4843'
    assert result.headers['Content-Type'] == 'image/jpeg'
    assert result.headers[
        'Content-Disposition'] == 'inline; filename="bnd-148x84.jpg"'


def test_scaled_image_download(appbrowser):
    path = '/politik/deutschland/2013-07/bnd/bnd-148x84.jpg'
    signature = sha1('80:60:time').hexdigest()      # we know the secret! :)
    result = appbrowser.get('/bitblt-80x60-' + signature + path)
    image = Image.open(StringIO(''.join(result.app_iter)))
    assert image.size == (80, 60)
    assert int(result.headers['Content-Length']) < 4843
    assert result.headers['Content-Type'] == 'image/jpeg'
    assert result.headers[
        'Content-Disposition'] == 'inline; filename="bnd-148x84.jpg"'


def test_scaled_image_download_with_bad_signature(appbrowser):
    path = '/politik/deutschland/2013-07/bnd/bnd-148x84.jpg'
    signature = sha1('80:60:foobar').hexdigest()      # we know the secret! :)
    result = appbrowser.get('/bitblt-80x60-' + signature + path)
    # bad signatures cause `repoze.bitblt` to do nothing;
    # we get the original image
    image = Image.open(StringIO(''.join(result.app_iter)))
    assert image.size == (148, 84)
    assert result.headers['Content-Length'] == '4843'
