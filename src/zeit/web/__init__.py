from zeit.web.core.decorator import dont_cache, reify, register_copyrights, \
    register_area, register_module, register_filter, register_ctxfilter, \
    register_envfilter, register_evalctxfilter, \
    register_global, register_ctxfunc, register_envfunc, \
    register_evalctxfunc, register_test


__import__('pkg_resources').declare_namespace(__name__)

__all__ = [
    'reify', 'register_copyrights', 'register_area', 'register_module',
    'register_filter', 'register_ctxfilter', 'register_envfilter',
    'register_evalctxfilter', 'register_global', 'register_ctxfunc',
    'register_envfunc', 'register_evalctxfunc', 'register_test',
    'dont_cache']
