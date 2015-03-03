import logging
import re

import lxml.etree
import zope.interface

import zeit.imp.source

import zeit.web.core.interfaces
import zeit.web.core.utils


video_series = None
log = logging.getLogger(__name__)


def get_video_series(series_source):
    try:
        series_xml = lxml.etree.parse(series_source)
    except (TypeError, IOError):
        return list()
    videoseries = series_xml.xpath('/allseries/videoseries/series')
    videoseries_list = list()
    for video in videoseries:
        url = video.xpath('@url')[0]
        title = video.xpath('@title')[0]
        videoseries_list.append(dict(url=url, title=title))
    return videoseries_list


class ScaleSource(zeit.imp.source.ScaleSource):

    def isAvailable(self, *args):  # NOQA
        # Contrary to CMS behavior, we do not want to hide any image scales
        # in zeit.web, so availability is `True` regardless of context.
        return True


class ImageScales(dict):

    zope.interface.implements(zeit.web.core.interfaces.IImageScales)

    def __init__(self, *args, **kw):
        sub = lambda x: int(re.sub('[^0-9]', '', '0' + str(x)))
        scales = {s.name: (sub(s.width), sub(s.height)) for s in
                  ScaleSource()('')}
        super(ImageScales, self).__init__(scales)


class TeaserMapping(dict):

    zope.interface.implements(zeit.web.core.interfaces.ITeaserMapping)

    _map = {'zon-large': ['leader', 'leader-two-columns', 'leader-panorama'],
            'zon-small': ['text-teaser', 'buttons', 'large', 'short', 'date'],
            'zon-fullwidth': ['leader-fullwidth'],
            'zon-parquet-large': ['parquet-large'],
            'zon-parquet-small': ['parquet-regular'],
            'hide': ['archive-print-volume', 'archive-print-year',
                     'two-side-by-side', 'ressort', 'leader-upright',
                     'buttons-fullwidth', 'parquet-printteaser',
                     'parquet-verlag']}

    def __init__(self, *args, **kw):
        # Flattens and reverses _map, so we can easily lookup a layout.
        super(TeaserMapping, self).__init__(
            x for k, v in self._map.iteritems() for x in zip(v, [k] * len(v)))
