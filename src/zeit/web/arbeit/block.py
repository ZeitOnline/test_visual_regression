import grokcore.component
import zeit.web
import zeit.web.core.block
import zeit.web.core.interfaces
import zeit.web.site.area.rss


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.arbeit.interfaces.IJobboxTicker)
class JobboxTicker(zeit.web.core.block.Block):

    @zeit.web.reify
    def content(self):
        return self.context.jobbox_ticker

    @zeit.web.reify
    def items(self):
        return list(zeit.web.site.area.rss.parse_feed(
            self.content.feed_url, 'jobbox_ticker'))

    @zeit.web.reify
    def teaser_text(self):
        return self.content.teaser

    @zeit.web.reify
    def landing_page_url(self):
        return self.content.landing_url
