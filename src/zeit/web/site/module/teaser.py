import grokcore.component
import zope.component

import zeit.web.site.module


# Since we register for 'teaser', we can implicitly assume that context
# provides zeit.content.cp.interfaces.ITeaserBlock, since 'teaser' is its
# context.type.
@zeit.web.register_module('teaser')
def dispatch_teaser_via_contenttype(context):
    try:
        teaser = list(context)[0]
    except (IndexError, TypeError):
        return context

    return zope.component.getMultiAdapter(
        (context, teaser), zeit.web.core.interfaces.IBlock)


@grokcore.component.adapter(
    zeit.content.cp.interfaces.ITeaserBlock,
    zeit.cms.interfaces.ICMSContent)
@grokcore.component.implementer(zeit.web.core.interfaces.IBlock)
def default_teaser(block, content):
    return block


@grokcore.component.adapter(
    zeit.content.cp.interfaces.ITeaserBlock,
    zeit.content.cp.interfaces.IStoryStream)
class StoryStreamTeaserBlock(
        zeit.web.site.module.Module,
        grokcore.component.MultiAdapter):

    grokcore.component.provides(zeit.web.core.interfaces.IBlock)

    def __init__(self, module, content):
        self.context = module
        self.storystream = content
        # NOTE: This means we ignore the teaser layout set by the user!
        self.layout = 'storystream'

    def __iter__(self):
        return iter(self.context)
