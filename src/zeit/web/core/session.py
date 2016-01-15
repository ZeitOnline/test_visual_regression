import binascii
import os
import time

from dogpile.cache.api import NO_VALUE
from pyramid.compat import PY3, text_
from pyramid.session import manage_accessed, manage_changed
import pyramid.interfaces
import zope.interface
import zope.component

import zeit.web.core.cache
import zeit.web.core.interfaces


SESSION_CACHE = zeit.web.core.cache.get_region('session')


def time_now():
    return int(time.time())


@zope.interface.implementer(pyramid.interfaces.ISession)
class CacheSession(dict):
    """Stores session data server-side in memcache, using the SSO cookie value
    as the key."""

    _dirty = False

    def __init__(self, request):
        self.request = request

        stored = SESSION_CACHE.get(
            self.session_id) if self.session_id else NO_VALUE
        if stored is not NO_VALUE:
            super(CacheSession, self).__init__(stored)
        else:
            now = time_now()
            self.created = now
            self.accessed = now
            self.renewed = now

    @property
    def created(self):
        return super(CacheSession, self).get('created')

    @created.setter
    def created(self, value):
        super(CacheSession, self).__setitem__('created', value)

    @property
    def accessed(self):
        return super(CacheSession, self).get('accessed')

    @accessed.setter
    def accessed(self, value):
        super(CacheSession, self).__setitem__('accessed', value)

    @property
    def renewed(self):
        return super(CacheSession, self).get('renewed')

    @renewed.setter
    def renewed(self, value):
        super(CacheSession, self).__setitem__('renewed', value)

    @zeit.web.reify
    def _reissue_time(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        if 'session.reissue_time' not in conf:
            return None
        return int(conf['session.reissue_time'])

    @zeit.web.reify
    def session_id(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        return self.request.cookies.get(conf.get('sso_cookie'))

    def persist(self):
        if not self.session_id or not self._dirty:  # not dirty only for tests
            return
        SESSION_CACHE.set(self.session_id, dict(self))

    # ISession methods
    def changed(self):
        if not self._dirty:
            self._dirty = True
            self.renewed = time_now()

            def store_session(request, response):
                self.persist()
                self.request = None  # explicitly break cycle for GC
            self.request.add_response_callback(store_session)

    @manage_changed
    def invalidate(self):
        self.clear()

    # Everything below here is copy&paste from pyramid.session.CookieSession,
    # the factory function pattern there does not allow us to inherit, sigh.

    # non-modifying dictionary methods
    get = manage_accessed(dict.get)
    __getitem__ = manage_accessed(dict.__getitem__)
    items = manage_accessed(dict.items)
    values = manage_accessed(dict.values)
    keys = manage_accessed(dict.keys)
    __contains__ = manage_accessed(dict.__contains__)
    __len__ = manage_accessed(dict.__len__)
    __iter__ = manage_accessed(dict.__iter__)

    if not PY3:
        iteritems = manage_accessed(dict.iteritems)
        itervalues = manage_accessed(dict.itervalues)
        iterkeys = manage_accessed(dict.iterkeys)
        has_key = manage_accessed(dict.has_key)

    # modifying dictionary methods
    clear = manage_changed(dict.clear)
    update = manage_changed(dict.update)
    setdefault = manage_changed(dict.setdefault)
    pop = manage_changed(dict.pop)
    popitem = manage_changed(dict.popitem)
    __setitem__ = manage_changed(dict.__setitem__)
    __delitem__ = manage_changed(dict.__delitem__)

    # flash API methods
    @manage_changed
    def flash(self, msg, queue='', allow_duplicate=True):
        storage = self.setdefault('_f_' + queue, [])
        if allow_duplicate or (msg not in storage):
            storage.append(msg)

    @manage_changed
    def pop_flash(self, queue=''):
        storage = self.pop('_f_' + queue, [])
        return storage

    @manage_accessed
    def peek_flash(self, queue=''):
        storage = self.get('_f_' + queue, [])
        return storage

    # CSRF API methods
    @manage_changed
    def new_csrf_token(self):
        token = text_(binascii.hexlify(os.urandom(20)))
        self['_csrft_'] = token
        return token

    @manage_accessed
    def get_csrf_token(self):
        token = self.get('_csrft_', None)
        if token is None:
            token = self.new_csrf_token()
        return token
