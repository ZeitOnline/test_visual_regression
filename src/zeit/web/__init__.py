from zeit.web.core.decorator import register_copyrights
from zeit.web.core.decorator import register_area
from zeit.web.core.decorator import register_filter
from zeit.web.core.decorator import register_global
from zeit.web.core.decorator import register_module
from zeit.web.core.decorator import register_test
from zeit.web.core.decorator import reify


__import__('pkg_resources').declare_namespace(__name__)

__all__ = [
    'register_copyrights', 'register_area', 'register_filter',
    'register_global', 'register_module', 'register_test', 'reify'
]
