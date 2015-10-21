import zeit.web
import zeit.web.core.utils


def test_new_style_interface_should_convert_base_types(application):
    iface = zeit.web.core.utils.INewStyle
    assert isinstance(iface([1, 2, 3]), zeit.web.nslist)
    assert isinstance(iface((1, 2, 3)), zeit.web.nstuple)
    assert isinstance(iface({'a': 'b'}), zeit.web.nsdict)
    assert isinstance(iface({1, 2, 3}), zeit.web.nsset)
    assert isinstance(iface('lorem'), zeit.web.nsstr)
    assert isinstance(iface(u'ipsum'), zeit.web.nsunicode)


def test_new_style_none_should_behave_like_expected(application):
    assert zeit.web.core.utils.INewStyle(None) is zeit.web.NSNone
    assert not zeit.web.NSNone
    assert zeit.web.NSNone == zeit.web.NSNone
    assert zeit.web.NSNone == None  # NOQA
    assert zeit.web.NSNone != 42
    assert repr(zeit.web.NSNone) == 'NSNone'
    assert str(zeit.web.NSNone) == ''
