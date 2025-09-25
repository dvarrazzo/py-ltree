from __future__ import annotations

import re
from uuid import UUID
from typing import Any, TypeAlias
from collections import namedtuple
from collections.abc import Sequence

from typing_extensions import Self

re_lquery = re.compile(r"^[a-zA-Z0-9_\|]+$")

LqueryItem: TypeAlias = "str | Star | Lquery"


class Star(namedtuple("Star", "min max")):
    def __new__(cls, min: int | None = None, max: int | None = None) -> Self:
        min = None if not min else int(min)
        max = None if not max else int(max)
        self = super(Star, cls).__new__(cls, min, max)
        return self

    re_star = re.compile(
        r"""
        ^ (?:
              (\*)
            | (?: \* \{ (\d+) \} )
            | (?: \* \{ (\d*) , (\d*) \} )
        ) $""",
        re.VERBOSE,
    )

    @classmethod
    def parse(cls, s: str) -> Self | None:
        m = cls.re_star.match(s)
        if m is None:
            return None

        if m.group(1):
            min = max = None
        elif m.group(2):
            min = max = int(m.group(2))
        else:
            v = m.group(3)
            min = int(v) if v else None
            v = m.group(4)
            max = int(v) if v else None

        return cls(min, max)

    def merge(self, other: Star) -> Star:
        min = ((self.min or 0) + (other.min or 0)) or None
        max = None if (self.max is None or other.max is None) else self.max + other.max
        return Star(min, max)

    def __str__(self) -> str:
        if self.min is None and self.max is None:
            return "*"
        if self.min is not None and self.max is not None:
            if self.min == self.max:
                return "*{%d}" % (self.min,)
            else:
                return "*{%d,%d}" % (self.min, self.max)
        if self.min is not None:
            return "*{%d,}" % (self.min,)
        if self.max is not None:
            return "*{,%d}" % (self.max,)

        assert False, "wat?"


class Lquery(tuple[LqueryItem]):
    """Wrapper for the Lquery data type."""

    __slots__ = ()

    def __new__(cls, *args: str | UUID | Star | Lquery | None) -> Self:
        def _label(s: Any) -> LqueryItem | None:
            if s is None or s == "":
                return None
            if isinstance(s, str):
                if re_lquery.match(s):
                    return s

                star = Star.parse(s)
                if star is not None:
                    return star

                raise ValueError("lquery label not valid: %s" % s)
            elif isinstance(s, UUID):
                return _label(str(s).lower().replace("-", "_"))
            else:
                return _label(str(s))

        labels: list[LqueryItem | None] = []

        for arg in args:
            if isinstance(arg, str):
                labels.extend(_label(i) for i in arg.split("."))
            elif isinstance(arg, Sequence):
                labels.extend(_label(i) for i in arg)
            else:
                labels.append(_label(arg))

        return tuple.__new__(cls, cls._merge_labels(labels))  # type: ignore[type-var]

    @classmethod
    def _merge_labels(cls, labels: list[LqueryItem | None]) -> list[LqueryItem]:
        rv: list[LqueryItem] = []
        for label in labels:
            if label is None:
                continue
            if not rv:
                rv.append(label)
                continue
            if isinstance(rv[-1], Star) and isinstance(label, Star):
                rv[-1] = rv[-1].merge(label)
            else:
                rv.append(label)

        return rv

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Lquery):
            return tuple.__eq__(self, other)
        elif isinstance(other, str):
            return str(self) == other
        else:
            return self.__eq__(Lquery(other))

    def __hash__(self) -> int:
        return hash(self)

    def __add__(self, other: Any) -> Lquery:
        return Lquery(self, other)

    def __radd__(self, other: Any) -> Lquery:
        return Lquery(other, self)

    def __repr__(self) -> str:
        return "%s(%r)" % (
            self.__class__.__name__,
            ".".join(str(i) for i in self),
        )

    def __str__(self) -> str:
        return str(".".join(str(i) for i in self))

    def __getitem__(self, i) -> LqueryItem:  # type: ignore
        if not isinstance(i, slice):
            return tuple.__getitem__(self, i)  # type: ignore
        else:
            return Lquery(tuple.__getitem__(self, i))  # type: ignore[arg-type]
