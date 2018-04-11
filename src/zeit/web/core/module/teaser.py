import grokcore.component
import zope.component

import zeit.cms.content.interfaces
import zeit.content.cp.interfaces

import zeit.web
import zeit.web.core.interfaces
import zeit.web.core.template


class TeaserBlock(grokcore.component.MultiAdapter):

    grokcore.component.baseclass()
    grokcore.component.provides(zeit.web.core.interfaces.IBlock)

    override_layout_id = None

    def __init__(self, module, content):
        self.module = module
        self._v_first_content = content

    def __getattr__(self, name):
        return getattr(self.module, name)

    # Sigh, proxying would be so much easier if __getattr__ could catch these.
    def __len__(self):
        return len(self.module)

    def __iter__(self):
        return iter(self.module)

    @zeit.web.reify
    def __name__(self):
        return self.module.__name__

    @property
    def force_mobile_image(self):
        if (zeit.cms.content.interfaces.ICommonMetadata.providedBy(
                self._v_first_content) and (
                self._v_first_content.access == 'abo')):
            return True
        elif zeit.web.core.template.branding(
                self._v_first_content) == 'brandeins':
            return True
        return super(TeaserBlock, self).force_mobile_image

    @force_mobile_image.setter
    def force_mobile_image(self, value):
        super(TeaserBlock, self).force_mobile_image = value

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
        return super(TeaserBlock, self).layout


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


@zeit.web.register_module('auto-teaser')
def module_for_auto_teaser(context):
    return dispatch_teaser_via_contenttype(context)


@grokcore.component.adapter(
    zeit.content.cp.interfaces.ITeaserBlock,
    zeit.cms.interfaces.ICMSContent)
class ContentTeaserBlock(TeaserBlock):

    @property
    def layout(self):
        # XXX This special case doesn't really belong here, but we have no
        # interface to help us register a separate adapter.
        if not (zeit.content.cp.interfaces.IStoryStream.providedBy(
                zeit.content.cp.interfaces.ICenterPage(self))):
            return super(ContentTeaserBlock, self).layout
        if (zeit.cms.content.interfaces.ICommonMetadata.providedBy(
                self._v_first_content) and
                self._v_first_content.tldr_milestone):
            self.override_layout_id = 'zon-milestone'
        return super(ContentTeaserBlock, self).layout


@grokcore.component.adapter(
    zeit.content.cp.interfaces.ITeaserBlock,
    zeit.content.article.interfaces.IArticle)
class ArticleTeaserBlock(ContentTeaserBlock):

    @property
    def liveblog(self):
        if zeit.web.core.template.liveblog(self._v_first_content):
            return zeit.web.core.interfaces.ILiveblogInfo(
                self._v_first_content)
