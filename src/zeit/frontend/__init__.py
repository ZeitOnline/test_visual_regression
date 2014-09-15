from . import decorator


__all__ = [
    'COMMENT_COLLECTION_PATH', 'COMMENT_PATH', 'COMMENT_ID_PREFIX',
    'register_filter', 'register_global', 'register_test',
    'register_copyrights', 'reify'
]

COMMENT_COLLECTION_PATH = u'/-/comments/collection/*'
COMMENT_PATH = u'/-/comments/{cid}'
COMMENT_ID_PREFIX = u'http://xml.zeit.de'

register_filter = decorator.JinjaEnvRegistrator('filters')
register_global = decorator.JinjaEnvRegistrator('globals')
register_test = decorator.JinjaEnvRegistrator('tests')

register_copyrights = decorator.register_copyrights
reify = decorator.reify
