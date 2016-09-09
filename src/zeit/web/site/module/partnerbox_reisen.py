import grokcore.component

import zeit.cms.interfaces
import zeit.content.image.interfaces

import zeit.web
import zeit.web.core.centerpage


@zeit.web.register_module('partnerbox_reisen')
class PartnerboxReisen(zeit.web.core.centerpage.Module):

    def __init__(self, context):
        super(PartnerboxReisen, self).__init__(context)
        self.layout.image_pattern = 'wide'
        self.href = (
            'http://zeitreisen.zeit.de/?wt_mc=zr.intern.display.zeit_online.'
            'reisebox.dynamisch.widget.widget&utm_source=zeit_online&utm_med'
            'ium=display&utm_campaign=reisebox_dynamisch&utm_content=widget')


@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
@grokcore.component.adapter(PartnerboxReisen)
class PartnerboxReisenImages(object):

    def __init__(self, context):
        self.context = context
        self.fill_color = None
        self.image = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/angebote/reisen/reisebox-image/', None)
