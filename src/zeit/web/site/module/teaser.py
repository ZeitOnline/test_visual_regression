import grokcore.component
import zope.component

import zeit.content.cp.interfaces

import zeit.web.core.centerpage


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
        zeit.web.core.centerpage.Module,
        grokcore.component.MultiAdapter):

    grokcore.component.provides(zeit.web.core.interfaces.IBlock)

    def __init__(self, module, content):
        self.context = module
        self.storystream = content
        # NOTE: This means we ignore the teaser layout set by the user!
        self.layout = 'storystreamteaser'
        self.article_modules = self.get_articles(
            3, zeit.content.cp.interfaces.ITeaserBlock)

    def __iter__(self):
        return iter(self.context)

    def get_articles(self, article_number, *teaserable_atom_types):
        articles = []

        regions = self.storystream.values()
        for region in regions:
            areas = region.values()
            for area in areas:
                for module in area.select_modules(*teaserable_atom_types):
                    articles.append(module)
                    if (len(articles) >= article_number):
                        return articles

        return articles


# XXX The Article/infobox block has been adjusted so we can reuse it as a
# CP/teaser module. We should instead discard the current article block
# mechanics and use the CP modules one there, too.
@grokcore.component.adapter(
    zeit.content.cp.interfaces.ITeaserBlock,
    zeit.content.infobox.interfaces.IInfobox)
class InfoboxTeaserBlock(
        zeit.web.core.centerpage.Module,
        zeit.web.core.block.Infobox,
        grokcore.component.MultiAdapter):

    grokcore.component.provides(zeit.web.core.interfaces.IBlock)

    def __init__(self, module, content):
        self.module = module
        self.context = content

    @property
    def layout(self):
        return self.module.layout
