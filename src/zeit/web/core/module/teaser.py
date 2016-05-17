import grokcore.component
import zope.component

import zeit.content.cp.interfaces

import zeit.web
import zeit.web.core.interfaces


class LayoutOverrideTeaserBlock(zeit.content.cp.blocks.teaser.TeaserBlock,
                                grokcore.component.MultiAdapter):

    grokcore.component.baseclass()
    grokcore.component.provides(zeit.web.core.interfaces.IBlock)

    override_layout_id = None

    def __init__(self, module, content):
        super(LayoutOverrideTeaserBlock, self).__init__(
            module.__parent__, module.xml)
        self._v_first_content = content

    @property
    def layout(self):
        if self.override_layout_id:
            source = zeit.content.cp.interfaces.ITeaserBlock['layout'].source(
                self)
            layout = source.find(self.override_layout_id)
            if layout:
                return layout
            else:
                id = self.override_layout_id
                return zeit.content.cp.layout.BlockLayout(
                    id, id, areas=[], image_pattern=id)
        return super(LayoutOverrideTeaserBlock, self).layout


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
