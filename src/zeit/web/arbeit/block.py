# -*- coding: utf-8 -*-

import grokcore.component
import zeit.web.core.block
import zeit.web.core.interfaces
import zeit.web.site.area.rss


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.arbeit.interfaces.IJobboxTicker)
class JobboxTicker(zeit.web.core.block.Block):

    def __init__(self, model_block):
        self.source_obj = model_block.jobbox
        self.items = zeit.web.site.area.rss.parse_feed(
            self.source_obj.feed_url, 'jobbox_ticker')

    @zeit.web.reify
    def teaser_text(self):
        return self.source_obj.teaser

    @zeit.web.reify
    def landing_page_url(self):
        return self.source_obj.landing_url
