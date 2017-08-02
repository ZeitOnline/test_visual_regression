import grokcore.component

import zeit.content.cp.interfaces
import zeit.arbeit.interfaces

import zeit.web.core.module.teaser
import zeit.web.site.module.teaser


@grokcore.component.adapter(
    zeit.content.cp.interfaces.ITeaserBlock,
    zeit.arbeit.interfaces.IZARInfobox)
class ZARInfoboxTeaserBlock(zeit.web.site.module.teaser.InfoboxTeaserBlock):
    pass
