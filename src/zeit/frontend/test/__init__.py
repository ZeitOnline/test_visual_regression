# -*- coding: utf-8 -*-
import exceptions

from .browser import Browser

__all__ = ['Browser', 'Raiser', 'raise_exc']


class Raiser(object):
    """Testing purpose class for raising any of Python's builtin exceptions.
    Properties with a camel-cased variant of the exception's name raise the
    corresponding Exception on access.
    Usage examples:

        Raiser().key_error
        Raiser().system_exit
    """
    def __getattr__(self, name):
        cls = ''.join(x.capitalize() or '_' for x in name.split('_'))
        if not hasattr(exceptions, cls):
            return super(Raiser, self).__getattr__(name)
        raise getattr(exceptions, cls)()


def raise_exc(exc, *args):
    """Helper function for raising exceptions without using the builtin
    `raise` statement."""
    raise exc(*args)
