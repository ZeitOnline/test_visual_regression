# Class to rule banner.xml
# in the place to be
#
# We want to get out per view:
# Array of active Places per page?
#
# we'll need: the list of possible Places
# and the rules to add Places to pages
#
# Structure:
# {
#   'name': 'tile_1', // name to refer to in contact with iqd, i.e. tile_1
#   'tile': '1',
#   'sizes': ['728x90'], // array of possible sizes
#   'dcopt': 'ist', // voodoo
#   'label': 'anzeige', // Text to display before the ad
#   'noscript_width_height': ('728', '90'), // which of the sizes is used for noscript?
#   'diuqilon': True, // negative keyword targeting
#   'min_width': 768, // window width, negative keyword targeting is applied to
# }
class Place:

    def __init__(self, banner):
        self.banner = banner

