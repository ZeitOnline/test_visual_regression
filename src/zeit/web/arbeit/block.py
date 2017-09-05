# -*- coding: utf-8 -*-

import grokcore.component
import zeit.web.core.block
import zeit.web.core.interfaces
import zeit.web.site.area.rss


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.arbeit.interfaces.IJobboxTicker)
class JobboxTicker(zeit.web.core.block.Block):

    def __init__(self, model_block):
        self.model_block = model_block.jobbox_ticker
        self.items = zeit.web.site.area.rss.parse_feed(
            self.model_block.feed_url, 'jobbox_ticker')

    @zeit.web.reify
    def teaser_text(self):
        return self.model_block.teaser

    @zeit.web.reify
    def landing_page_url(self):
        return self.model_block.landing_url
