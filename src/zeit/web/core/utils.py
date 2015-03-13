import collections
import re


__all__ = ['defaultdict', 'nslist', 'nstuple', 'nsdict', 'nsset', 'nsstr',
           'nsunicode']


class defaultdict(collections.defaultdict):
    """Extension of stdlib's defaultdict that overwrites its `get` method and
    behaviour of the `in` operator.
    """

    def get(self, key, *args):
        """If the key cannot be found, return the (optional) function scope
        default or the defaultdict instances default.

        :param key: Key of the dictionary item to be retrieved.
        :param default: Opional function scope default value.
        """
        length = len(args)
        if length > 1:
            raise TypeError('defaultdict expected at most 2 arguments, got %s'
                            % length)
        elif length == 1:
            return super(defaultdict, self).get(key) or args[0]
        return self.__getitem__(key)

    def __contains__(self, name):
        """Instances of defaultdict will pretend to contain any key."""
        return True


def fix_misrepresented_latin(val):
    """Fix misrepresentation of latin-1 chars in unicode strings."""

    if isinstance(val, unicode):
        try:
            val = val.encode('latin-1', 'backslashreplace').decode('utf-8')
        except UnicodeDecodeError:
            pass
    return val


def to_int(value, pattern=re.compile(r'[^\d.]+')):
    """Converts an arbitrary object with a unicode representation to an int
    by trashing all non-decimal characters.

    :param value: Arbitrary input
    :rtype: int
    """

    return int(pattern.sub('', unicode(value, errors='ignore')))


def neighborhood(iterable, default=None):
    """Sliding window generator function that yields a tuple in the form
    of (prev, item, next).
    :param iterable: Iterable to cycle through
    :param default: Default value to yield for undefined neighbors
    :rtype: types.GeneratorType
    """

    iterator = iter(iterable)
    prev, item = default, iterator.next()
    for next in iterator:
        yield prev, item, next
        prev, item = item, next
    yield prev, item, default


class nsmixin:
    """New style magic attribute methods as a mixin class."""

    __setattr__ = object.__setattr__
    __delattr__ = object.__delattr__


class nslist(list, nsmixin):
    """New style list class with attribute access and manipulation."""

    pass


class nstuple(tuple, nsmixin):
    """New style tuple class with attribute access and manipulation."""

    pass


class nsdict(dict, nsmixin):
    """New style dictionary class with attribute access and manipulation."""

    pass


class nsset(set, nsmixin):
    """New style set class with attribute access and manipulation."""

    pass


class nsstr(str, nsmixin):
    """New style string class with attribute access and manipulation."""

    pass


class nsunicode(unicode, nsmixin):
    """New style unicode class with attribute access and manipulation."""

    pass


class frozendict(dict):
    """Custom dictionary class that discourages item manipulation."""

    __delitem__ = __setitem__ = clear = pop = popitem = setdefault = update = (
        NotImplemented)


class attrdict(dict):
    """Custom dictionary class that allows item access via attribute names."""

    def __getattr__(self, key):
        return key in self and self[key] or self.__getattribute__(key)
