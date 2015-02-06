import lxml.etree

video_series = None


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
