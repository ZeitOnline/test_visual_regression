# NOTE: Transitionary construction only, remove once TMS is fully in production
# and the `zeit.retresco.tms` ZCML feature has been retired.
import grokcore.component as grok

import zeit.cms.repository.interfaces
import zeit.cms.tagging.interfaces
import zeit.intrafind.tagger
import zeit.intrafind.whitelist
import zeit.retresco.tagger
import zeit.retresco.whitelist

import zeit.web.core.application


@grok.adapter(zeit.cms.repository.interfaces.IDAVContent)
@grok.implementer(zeit.cms.tagging.interfaces.ITagger)
def tagger(context):
    if zeit.web.core.application.FEATURE_TOGGLES.find('topicpages_tms'):
        return zeit.retresco.tagger.Tagger(context)
    else:
        return zeit.intrafind.tagger.Tagger(context)


class Whitelist(grok.GlobalUtility):

    grok.implements(zeit.cms.tagging.interfaces.IWhitelist)

    def __getattr__(self, name):
        if zeit.web.core.application.FEATURE_TOGGLES.find('topicpages_tms'):
            origin = RETRESCO_WHITELIST
        else:
            origin = INTRAFIND_WHITELIST
        return getattr(origin, name)


class Topicpages(grok.GlobalUtility):

    grok.implements(zeit.cms.tagging.interfaces.ITopicpages)

    def __getattr__(self, name):
        if zeit.web.core.application.FEATURE_TOGGLES.find('topicpages_tms'):
            origin = RETRESCO_TOPICPAGES
        else:
            origin = INTRAFIND_TOPICPAGES
        return getattr(origin, name)


RETRESCO_WHITELIST = zeit.retresco.whitelist.Whitelist()
INTRAFIND_WHITELIST = zeit.intrafind.whitelist.Whitelist()

RETRESCO_TOPICPAGES = zeit.retresco.whitelist.Topicpages()
INTRAFIND_TOPICPAGES = zeit.intrafind.whitelist.Topicpages()
