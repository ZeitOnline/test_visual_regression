from zeit.web.core.decorator import reify, register_copyrights, \
    register_area, register_module, register_filter, register_ctxfilter, \
    register_envfilter, register_evalctxfilter, hit_for_pass, \
    register_global, register_ctxfunc, register_envfunc, \
    register_evalctxfunc, register_test

from zeit.web.core.utils import INewStyle, NSNone, attrdict, defaultattrdict, \
    defaultdict, frozendict, nsdict, nslist, nsset, nsstr, nstuple, nsunicode

__import__('pkg_resources').declare_namespace(__name__)

__all__ = [
    'reify', 'register_copyrights', 'register_area', 'register_module',
    'register_filter', 'register_ctxfilter', 'register_envfilter',
    'register_evalctxfilter', 'register_global', 'register_ctxfunc',
    'register_envfunc', 'register_evalctxfunc', 'register_test',
    'INewStyle', 'NSNone', 'attrdict', 'defaultattrdict', 'defaultdict',
    'frozendict', 'nsdict', 'nslist', 'nsset', 'nsstr', 'nstuple', 'nsunicode',
    'hit_for_pass'
]
