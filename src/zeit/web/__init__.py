# -*- coding: utf-8 -*-

import pkg_resources

from .core import decorator


pkg_resources.declare_namespace(__name__)

__all__ = [
    'register_copyrights', 'register_filter', 'register_global',
    'register_module', 'register_test', 'reify'
]

register_filter = decorator.JinjaEnvRegistrator('filters')
register_global = decorator.JinjaEnvRegistrator('globals')
register_test = decorator.JinjaEnvRegistrator('tests')

register_copyrights = decorator.register_copyrights
register_module = decorator.register_module
reify = decorator.reify
