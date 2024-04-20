from __future__ import annotations

import re
from functools import total_ordering
from collections.abc import Sequence

from typing import Any

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

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Ltree):
            return tuple.__eq__(self, other)
        elif isinstance(other, str):
            return str(self) == other
        else:
            return self.__eq__(Ltree(other))

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Ltree):
            return tuple.__lt__(self, other)
        elif isinstance(other, str):
            return str(self) < other
        else:
            return self.__lt__(Ltree(other))

    def __hash__(self) -> int:
        return hash(self)

    def __add__(self, other: Any) -> Ltree:
        return Ltree(self, other)

    def __radd__(self, other) -> Ltree:
        return Ltree(other, self)

    def __repr__(self) -> str:
        return "%s(%r)" % (
            self.__class__.__name__,
            ".".join(str(i) for i in self),
        )

    def __str__(self) -> str:
        return str(".".join(str(i) for i in self))

    def __getslice__(self, i, j):
        """Python 2 compatibility function."""
        return self.__getitem__(slice(i, j))

    def __getitem__(self, i):
        if not isinstance(i, slice):
            return tuple.__getitem__(self, i)
        else:
            return Ltree(tuple.__getitem__(self, i))
