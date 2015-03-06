# -*- coding: utf-8 -*-

from .core import decorator

__import__('pkg_resources').declare_namespace(__name__)


__all__ = [
    'register_filter', 'register_global', 'register_test',
    'register_copyrights', 'reify'
]

register_filter = decorator.JinjaEnvRegistrator('filters')
register_global = decorator.JinjaEnvRegistrator('globals')
register_test = decorator.JinjaEnvRegistrator('tests')

register_copyrights = decorator.register_copyrights
reify = decorator.reify
