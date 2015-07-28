import lxml.objectify
import mock
import zope.component

import zeit.content.cp.automatic
import zeit.content.cp.interfaces

import zeit.web.site.area.overview
import zeit.web.core.utils


def get_area(kind, values=0, attrs={'visible': 'true', 'hide-dupes': 'true'}):
    context = mock.MagicMock()
    context.xml = xml = lxml.objectify.E.element(**attrs)
    context.automatic = False
    context.__parent__ = None
    cls = zeit.content.cp.blocks.automatic.AutomaticTeaserBlock
    context.values.return_value = [cls(context, xml) for _ in range(values)]
    area = zeit.content.cp.automatic.AutomaticArea(context)
    return zope.component.getAdapter(
        area, zeit.content.cp.interfaces.IRenderedArea, kind)


def test_overview_area_should_have_a_sanity_bound_count(application):
    area = get_area('overview')
    assert area.count == zeit.web.site.area.overview.SANITY_BOUND


def test_overview_area_should_not_overflow_if_unnecessary(application):
    area = get_area('overview')
    area.hits = 3
    assert len(list(area.placeholder)) == 0

    area = get_area('overview', 3)
    area.hits = 3
    assert len(list(area.placeholder)) == 3


def test_overview_area_should_respect_overflow_sanity_bound(
        application, monkeypatch):
    monkeypatch.setattr(zeit.web.site.area.overview, 'SANITY_BOUND', 5)
    area = get_area('overview', 1)
    area.hits = 10
    assert len(list(area.placeholder)) == 5


def test_overview_area_clone_factory_should_set_proper_attributes():
    class Foo(mock.Mock):
        __parent__ = object()
        __name__ = object()
        xml = object()

    clones = zeit.web.site.area.overview.Overview.clone_factory(Foo(), 3)

    assert all(c.xml is Foo.xml for c in clones)
    assert all(c.__parent__ is Foo.__parent__ for c in clones)
    assert all(len(c.__name__) == 36 for c in clones)


def test_ranking_area_should_iterate_placeholders(application):
    area = get_area('ranking', 3)
    area.hits = 10
    assert len(list(area.placeholder)) == 3
