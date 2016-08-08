import zeit.cms.interfaces

import zeit.web
import zeit.web.core.centerpage


@zeit.web.register_module('partnerbox_reisen')
class PartnerboxReisen(zeit.web.core.centerpage.Module):

    @zeit.web.reify
    def image(self):
        return zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/zeit-online/image/filmstill-hobbit-schlacht-fuenf-hee/', None)
        #    'http://xml.zeit.de/angebote/reisen/reisebox-image', None)
