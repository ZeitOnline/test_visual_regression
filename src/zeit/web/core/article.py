import grokcore.component
import zope.interface
import copy

import zeit.cms.repository.interfaces
import zeit.content.article
import zeit.content.article.article
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces

import zeit.web.core.block
import zeit.web.core.interfaces


@zope.interface.implementer(zeit.web.core.interfaces.IPage)
class Page(object):

    def __init__(self, division):
        self.number = division.number
        self.teaser = division.teaser or ''
        self.blocks = []

    def __iter__(self):
        return iter(self.blocks)

    def __len__(self):
        return len(self.blocks)

    def __getitem__(self, key):
        return self.blocks[key]

    def __setitem__(self, key, value):
        self.blocks[key] = value

    def __delitem__(self, key):
        del self.blocks[key]

    def append(self, block):
        block = zeit.web.core.interfaces.IFrontendBlock(block, None)
        if block is not None:
            self.blocks.append(block)


def _inject_banner_code(
        pages, advertising_enabled, is_longform, pubtype='zon'):
    """Injecting banner code in page.blocks counts and injects only after
    paragraphs, configured for zon, zmo, longforms... for now"""

    possible_pages = [i for i in xrange(1, len(pages) + 1)]
    banner_conf = {
        'zon': {
            'tiles': [7],  # banner tiles in articles
            'ad_paras': [2],  # paragraph(s) to insert ad after
            'content_ad_para': [4]  # paragraph/s to insert content ad after
        },
        'zmo': {
            'tiles': [7, 8],
            'ad_paras': [2, 6],
            'content_ad_para': [4]
        },
        'longform': {
            'tiles': [8],
            'ad_paras': [5]
        }
    }

    if is_longform:
        possible_pages = [2]  # page 1 is somehow the "intro text"
        pubtype = 'longform'

    if advertising_enabled:
        for i, page in enumerate(pages, start=1):
            if i in possible_pages:
                _place_adtag_by_paragraph(page,
                                          banner_conf[pubtype]['tiles'],
                                          banner_conf[pubtype]['ad_paras'])
                if not is_longform:
                    _place_content_ad_by_paragraph(
                        page, banner_conf[pubtype]['content_ad_para'])
    return pages


def _place_adtag_by_paragraph(page, tile_list, possible_paragraphs):
    paragraphs = filter(
        lambda b: isinstance(b, zeit.web.core.block.Paragraph), page.blocks)

    for index, pp in enumerate(possible_paragraphs):
        if len(paragraphs) > pp + 1:
            try:
                _para = paragraphs[pp]
                for i, block in enumerate(page.blocks):
                    if _para == block:
                        t = tile_list[index] - 1
                        # save the (virtual) page nr on (copies) of the banner,
                        # to be able to handle banner display inside the macro.
                        banner = copy.copy(zeit.web.core.banner.banner_list[t])
                        setattr(banner, 'on_page_nr', int(page.number + 1))
                        page.blocks.insert(i, banner)
                        break
            except IndexError:
                pass


def _place_content_ad_by_paragraph(page, possible_paragraphs):
    paragraphs = filter(
        lambda b: isinstance(b, zeit.web.core.block.Paragraph), page.blocks)
    content_ad = zeit.web.core.banner.ContentAdBlock("iq-artikelanker")

    for index, pp in enumerate(possible_paragraphs):
        if len(paragraphs) > pp + 1:
            try:
                _para = paragraphs[pp]
                for i, block in enumerate(page.blocks):
                    if _para == block:
                        page.blocks.insert(i, content_ad)
                        break
            except IndexError:
                pass


@grokcore.component.adapter(zeit.content.article.interfaces.IArticle)
@grokcore.component.implementer(zeit.web.core.interfaces.IPages)
def pages_of_article(context):
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    body.ensure_division()  # Old articles don't always have divisions.
    try:
        advertising_enabled = context.advertising_enabled
    except AttributeError:
        advertising_enabled = True
    try:
        is_longform = context.is_longform
    except AttributeError:
        is_longform = False
    # IEditableBody excludes the first division since it cannot be edited
    first_division = body.xml.xpath('division[@type="page"]')[0]
    first_division = body._get_element_for_node(first_division)

    pages = []
    page = Page(first_division)
    pages.append(page)
    blocks = body.values()
    # delete article image. it resides in its own property 'main_image_block'
    try:
        if zeit.content.article.edit.interfaces.IImage.providedBy(blocks[0]):
            del blocks[0]
    except IndexError:
        pass
    for block in blocks:
        if zeit.content.article.edit.interfaces.IDivision.providedBy(block):
            page = Page(block)
            pages.append(page)
        else:
            page.append(block)
    if zeit.magazin.interfaces.IZMOContent.providedBy(context):
        return _inject_banner_code(
            pages, advertising_enabled, is_longform, pubtype='zmo')
    return _inject_banner_code(pages, advertising_enabled, is_longform)


def convert_authors(article, is_longform=False):
    author_list = []
    try:
        author_ref = article.authorships
        for index, author in enumerate(author_ref):
            location = zeit.content.author.interfaces.IAuthorReference(
                author).location
            author = {
                'name': getattr(author.target, 'display_name', None),
                'href': getattr(author.target, 'uniqueId', None),
                'image_group': getattr(author.target, 'image_group', None),
                'prefix': u'', 'suffix': u'', 'location': u''}
            # add location
            if location and not is_longform:
                author['location'] = u', {}'.format(location)
            # add prefix
            if index == 0:
                if is_longform:
                    author['prefix'] = u'\u2014 von'
                else:
                    author['prefix'] = u' von'
            # add suffix
            if index == len(author_ref) - 2:
                author['suffix'] = u' und'
            elif index < len(author_ref) - 1:
                author['suffix'] = u', '
            author_list.append(author)
        return author_list
    except (IndexError, OSError):
        return []


class ILongformArticle(zeit.content.article.interfaces.IArticle):
    # TODO: Please remove when we have Longforms for ICMSContent
    pass


class IFeatureLongform(zeit.content.article.interfaces.IArticle):
    pass


class IShortformArticle(zeit.content.article.interfaces.IArticle):
    pass


class IColumnArticle(zeit.content.article.interfaces.IArticle):
    pass


class ILiveblogArticle(zeit.content.article.interfaces.IArticle):
    pass


class IPhotoclusterArticle(zeit.content.article.interfaces.IArticle):
    pass
