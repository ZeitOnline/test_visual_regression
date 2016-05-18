import grokcore.component

import zeit.content.cp.interfaces

import zeit.web.core.block
import zeit.web.core.centerpage
import zeit.web.core.interfaces
import zeit.web.core.module.teaser


@grokcore.component.adapter(
    zeit.content.cp.interfaces.ITeaserBlock,
    zeit.content.author.interfaces.IAuthor)
class AuthorTeaserBlock(zeit.web.core.module.teaser.LayoutOverrideTeaserBlock):

    @property
    def layout(self):
        if (self.xml.get('module') == 'zon-small' and
                self.__parent__.kind in ['duo', 'minor']):
            self.override_layout_id = 'zon-author'
        return super(AuthorTeaserBlock, self).layout


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
