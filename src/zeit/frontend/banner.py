from lxml import objectify
import urllib2
import zeit.frontend.interfaces
import zope.interface

#
# A place is a space on the website, which can
#   be filled with a banner
#
# @param string tile tilenumber as supplied in iqd speech
# @param array sizes in the form 'widthxheight' i.e. '728x90'
# @param bool diuqilon sets negative keyword targeting
# @param string label Label to be shown above the ad
# @keyparam int min_width window width negativ keyword targeting
#               is applied to, defaults to 0 (no min-width)
# @keyparam bool active deactivate the place by configuration if needed
# @keyparam string dcopt iqd keyword, defaults to 'ist'
#


@zope.interface.implementer(zeit.frontend.interfaces.IPlace)
class Place(object):

    def __init__(self, tile, sizes, diuqilon, label,
                 min_width=0, active=True, dcopt='ist'):
        self.name = 'tile_' + str(tile)
        self.tile = tile
        self.sizes = sizes
        self.diuqilon = diuqilon
        self.min_width = min_width
        self.dcopt = dcopt
        if label is not None:
            self.label = label
        if not isinstance(self.sizes, list) or self.sizes[0] is None:
            raise IndexError("Invalid Sizes Array")
        self.noscript_width_height = self.sizes[0].split('x')


@zope.interface.implementer(zeit.frontend.interfaces.IIqdMobileList)
class IqdMobileList(object):

    def __init__(self, iqd_id):
        self.cp = {}
        self.gallery = {}
        self.default = {}
        self.ressort = iqd_id.get('ressort')
        self.centerpage['top'] = iqd_id.centerpage.get('top')
        self.centerpage['bottom'] = iqd_id.centerpage.get('bottom')
        self.gallery['top'] = iqd_id.gallery.get('top')
        self.article['top'] = iqd_id.article.get('top')
        self.article['middle'] = iqd_id.article.get('middle')
        self.article['bottom'] = iqd_id.article.get('bottom')


banner_list = None
iqd_mobile_ids = None


def make_banner_list(banner_config):
    if not banner_config:
        return []
    banner_list = []
    file = urllib2.urlopen(banner_config)
    root = objectify.fromstring(file.read())
    for place in root.place:
        try:
            sizes = str(place.multiple_sizes).strip().split(',')
        except AttributeError:
            sizes = [str(place.width) + 'x' + str(place.height)]
        try:
            diuqilon = place.diuqilon
        except AttributeError:
            diuqilon = False
        try:
            adlabel = place.adlabel
        except AttributeError:
            adlabel = None
        banner_list.append(Place(
            place.tile, sizes, diuqilon, adlabel,
            min_width=place.min_width, active=place.get('active'),
            dcopt=place.dcopt))
    return sorted(banner_list, key=lambda place: place.tile)


def make_iqd_mobile_ids(banner_config):
    if not banner_config:
        return []
    iqd_mobile_ids = []
    file = urllib2.urlopen(banner_config)
    root = objectify.fromstring(file.read())
    for iqd_id in root.iqd_id:
        try:
            iqd_mobile_ids.append(IqdMobileList(iqd_id))
        except:
            pass
    return iqd_mobile_ids
