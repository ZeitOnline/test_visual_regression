import zeit.cms.interfaces
import zeit.content.cp.centerpage

import zeit.web.core.centerpage
import zeit.web.core.utils
import zeit.web.site.module.search_form


def test_get_module_filter_should_correctly_extract_cpextra_id(application):
    block = object()
    assert zeit.web.core.centerpage.get_module(block) is block

    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/suche/index')
    block = zeit.web.core.utils.find_block(cp, module='search-form')

    block.cpextra = 'n/a'
    module = zeit.web.core.centerpage.get_module(block)
    assert isinstance(module, zeit.web.core.centerpage.Module)
    assert module.layout.id == 'n/a'

    block.cpextra = 'search-form'
    module = zeit.web.core.centerpage.get_module(block)
    assert isinstance(module, zeit.web.site.module.search_form.Form)
    assert module.layout.id == 'search-form'


def test_teaser_layout_zon_square_should_be_adjusted_accordingly(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/feature/feature_longform')
    cp = zeit.content.cp.centerpage.CenterPage()
    area = cp.body.create_item('region').create_item('area')
    area.kind = 'duo'
    block = area.create_item('teaser')
    block.layout = zeit.content.cp.layout.get_layout('zon-square')
    block.append(article)

    module = zeit.web.core.centerpage.get_module(block)
    assert module.layout.id == 'zon-square'

    block.remove(article)
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/01')
    block.append(article)
    module = zeit.web.core.centerpage.get_module(block)
    assert module.layout.id == 'zmo-square'

    block.remove(article)
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/simple')
    block.append(article)
    module = zeit.web.core.centerpage.get_module(block)
    assert module.layout.id == 'zco-square'
