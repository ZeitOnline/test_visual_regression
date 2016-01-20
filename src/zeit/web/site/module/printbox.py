import logging

import zeit.cms.interfaces
import zeit.content.image.interfaces

import zeit.web
import zeit.web.core.module


log = logging.getLogger(__name__)


@zeit.web.register_module('printbox')
class Printbox(zeit.web.core.module.Module, list):

    def __init__(self, context):
        self.context = context

        box = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/angebote/print-box', None)

        if getattr(box, 'byline', '') == 'mo-mi':
            box = zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/angebote/angebotsbox')
            self.layout = 'angebotsbox'
        else:
            self.layout = 'printbox'

        if box is not None:
            self.append(box)

    @zeit.web.reify
    def image(self):
        try:
            return zeit.content.image.interfaces.IImages(self[0]).image
        except (TypeError, IndexError, AttributeError):
            return
