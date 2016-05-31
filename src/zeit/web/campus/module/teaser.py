import grokcore.component

import zeit.content.cp.interfaces
import zeit.campus.interfaces

import zeit.web.core.module.teaser


@grokcore.component.adapter(
    zeit.content.cp.interfaces.ITeaserBlock,
    zeit.campus.interfaces.IZCOContent)
class ZCOTeaserBlock(zeit.web.core.module.teaser.LayoutOverrideTeaserBlock):

    @property
    def layout(self):
        if self.xml.get('module') == 'zon-square':
            self.override_layout_id = 'zco-square'
        return super(ZCOTeaserBlock, self).layout
