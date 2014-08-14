import collections


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
        """Instances of defaultdict will pretend to contain all keys."""
        return True
