# -*- coding: utf-8 -*-
import requests


def test_gallery_seite_path_should_redirect_to_gallery_start(testserver):
    resp = requests.get('%s/zeit-online/gallery/biga_1/seite-3'
                        % testserver.url,
                        allow_redirects=False)
    assert(resp.headers['location'] ==
           '%s/zeit-online/gallery/biga_1' % testserver.url)
    assert resp.status_code == 301
