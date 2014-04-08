from lxml import etree
from lxml import objectify
import urllib2
import zeit.frontend.interfaces
import zope.interface
#
# Class to rule banner.xml
# in the place to be
#

#
# A place is a space on the website, which can
#   be filled with a banner
#
# @param string tile tilenumber as supplied in iqd speech
# @param array sizes in the form 'widthxheight' i.e. '728x90'
# @param bool diuqilon sets negative keyword targeting
# @keyparam string label Label to be shown above the ad, defaults to 'Anzeige'
# @keyparam int min_width window width negativ keyword targeting
#               is applied to, defaults to 0 (no min-width)
# @keyparam bool active deactivate the place by configuration if needed
# @keyparam string dcopt iqd keyword, defaults to 'ist'
#


@zope.interface.implementer(zeit.frontend.interfaces.IPlace)
class Place:

    def __init__(self, tile, sizes, diuqilon, label='Anzeige',
                 min_width=0, active=True, dcopt='ist'):
        self.name = 'tile_' + str(tile)
        self.tile = tile
        self.sizes = sizes
        self.diuqilon = diuqilon
        self.min_width = min_width
        self.dcopt = dcopt
        self.label = label
        if not isinstance(self.sizes, list) or self.sizes[0] is None:
            raise IndexError("Invalid Sizes Array")
        self.noscript_width_height = self.sizes[0].split('x')


banner_list = None


def make_banner_list(banner_config):
    banner_list = []
    file = urllib2.urlopen(banner_config)
    root = objectify.fromstring(file.read())
    for place in root.place:
        try:
            sizes = place.multiple_sizes.split(',').strip()
        except AttributeError:
            sizes = [str(place.width) + 'x' + str(place.height)]
        banner_list.append(Place(
            place.tile, sizes, None, label=place.adlabel,
            min_width=0, active=place.get('active'), dcopt=place.dcopt))
    return banner_list
