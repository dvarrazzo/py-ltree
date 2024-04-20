import re
from functools import total_ordering
from collections.abc import Sequence

re_ltree = re.compile(r"^[a-zA-Z0-9_]+$")


@total_ordering
class Ltree(tuple):
    """Wrapper for the Ltree data type."""

    __slots__ = ()

    def __new__(cls, *args):
        def _label(s):
            if s is None or s == "":
                return None
            if isinstance(s, str):
                if re_ltree.match(s):
                    return s
                else:
                    raise ValueError("ltree label not valid: %s" % s)
            else:
                return _label(str(s))

        labels = []

        for arg in args:
            if isinstance(arg, str):
                labels.extend(_label(i) for i in arg.split("."))
            elif isinstance(arg, Sequence):
                labels.extend(_label(i) for i in arg)
            else:
                labels.append(_label(arg))

        return tuple.__new__(cls, (label for label in labels if label is not None))

    def __eq__(self, other):
        if isinstance(other, Ltree):
            return tuple.__eq__(self, other)
        elif isinstance(other, str):
            return str(self) == other
        else:
            return self.__eq__(Ltree(other))

    def __lt__(self, other):
        if isinstance(other, Ltree):
            return tuple.__lt__(self, other)
        elif isinstance(other, str):
            return str(self) < other
        else:
            return self.__lt__(Ltree(other))

    def __hash__(self):
        return hash(self)

    def __add__(self, other):
        return Ltree(self, other)

    def __radd__(self, other):
        return Ltree(other, self)

    def __repr__(self):
        return "%s(%r)" % (
            self.__class__.__name__,
            ".".join(str(i) for i in self),
        )

    def __str__(self):
        return str(".".join(str(i) for i in self))

    def __getslice__(self, i, j):
        """Python 2 compatibility function."""
        return self.__getitem__(slice(i, j))

    def __getitem__(self, i):
        if not isinstance(i, slice):
            return tuple.__getitem__(self, i)
        else:
            return Ltree(tuple.__getitem__(self, i))

    # this *doesn't* work, because I'm an asshole: see psycopg bug #456
    # Now I have to write an adapter, register an adapter... sigh.
    # def __conform__(self, proto):
    #     import psycopg2.extensions as ext
    #     if issubclass(proto, ext.ISQLQuote):
    #         return ext.AsIs("'%s'" % self)
