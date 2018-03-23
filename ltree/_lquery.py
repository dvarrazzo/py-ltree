import re
from collections import Sequence, namedtuple

import six

re_lquery = re.compile(r'^[a-zA-Z0-9_\|]+$')


class Star(namedtuple('Star', 'min max')):
    def __new__(cls, min=None, max=None):
        min = None if not min else int(min)
        max = None if not max else int(max)
        self = super(Star, cls).__new__(cls, min, max)
        return self

    re_star = re.compile(r'''
        ^ (?:
              (\*)
            | (?: \* \{ (\d+) \} )
            | (?: \* \{ (\d*) , (\d*) \} )
        ) $''', re.VERBOSE)

    @classmethod
    def parse(cls, s):
        m = cls.re_star.match(s)
        if m is None:
            return None

        if m.group(1):
            min = max = None
        elif m.group(2):
            min = max = int(m.group(2))
        else:
            min = m.group(3)
            min = int(min) if min else None
            max = m.group(4)
            max = int(max) if max else None

        return cls(min, max)

    def merge(self, other):
        min = ((self.min or 0) + (other.min or 0)) or None
        max = None if (self.max is None or other.max is None) \
            else self.max + other.max
        return Star(min, max)

    def __str__(self):
        if self.min is None and self.max is None:
            return '*'
        if self.min is not None and self.max is not None:
            if self.min == self.max:
                return '*{%d}' % (self.min,)
            else:
                return '*{%d,%d}' % (self.min, self.max)
        if self.min is not None:
            return '*{%d,}' % (self.min,)
        if self.max is not None:
            return '*{,%d}' % (self.max,)

        assert False, 'wat?'


class Lquery(tuple):
    """Wrapper for the Lquery data type."""
    __slots__ = ()

    def __new__(cls, *args):
        def _label(s):
            if s is None or s == '':
                return None
            if isinstance(s, six.string_types):
                if re_lquery.match(s):
                    return s

                star = Star.parse(s)
                if star is not None:
                    return star

                raise ValueError('lquery label not valid: %s' % s)
            else:
                return _label(str(s))

        labels = []

        for arg in args:
            if isinstance(arg, six.string_types):
                labels += map(_label, arg.split('.'))
            elif isinstance(arg, Sequence):
                labels += map(_label, arg)
            else:
                labels.append(_label(arg))

        return tuple.__new__(cls, cls._merge_labels(labels))

    @classmethod
    def _merge_labels(cls, labels):
        rv = []
        for l in labels:
            if l is None:
                continue
            if not rv:
                rv.append(l)
                continue
            if isinstance(rv[-1], Star) and isinstance(l, Star):
                rv[-1] = rv[-1].merge(l)
            else:
                rv.append(l)

        return rv

    def __eq__(self, other):
        if isinstance(other, Lquery):
            return tuple.__eq__(self, other)
        elif isinstance(other, six.string_types):
            return str(self) == other
        else:
            return self.__eq__(Lquery(other))

    def __add__(self, other):
        return Lquery(self, other)

    def __radd__(self, other):
        return Lquery(other, self)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, '.'.join(map(str, self)))

    def __str__(self):
        return '.'.join(map(str, self))

    def __getslice__(self, i, j):
        return Lquery(tuple.__getslice__(self, i, j))

    def __getitem__(self, i):
        if not isinstance(i, slice):
            return tuple.__getitem__(self, i)
        else:
            return Lquery(tuple.__getitem__(self, i))
