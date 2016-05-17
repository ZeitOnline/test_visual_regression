import urlparse

import grokcore.component

import zeit.content.cp.interfaces
import zeit.magazin.interfaces

import zeit.web.core.module.teaser


@grokcore.component.adapter(
    zeit.content.cp.interfaces.ITeaserBlock,
    zeit.magazin.interfaces.IZMOContent)
class ZMOTeaserBlock(zeit.web.core.module.teaser.LayoutOverrideTeaserBlock):

    @property
    def layout(self):
        if self.xml.get('module') != 'zon-square':
            return super(ZMOTeaserBlock, self).layout

        # TODO: Remove when Longform will be generally used on www.zeit.de
        if not urlparse.urlparse(
                self._v_first_content.uniqueId).path.startswith('/feature/'):
            self.override_layout_id = 'zmo-square'

        return super(ZMOTeaserBlock, self).layout
