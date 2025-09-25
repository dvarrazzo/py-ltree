from __future__ import annotations

from typing import Any
from functools import cache

from psycopg import AsyncConnection, postgres
from psycopg.types import TypeInfo
from psycopg.abc import AdaptContext, Buffer
from psycopg.adapt import Dumper, Loader

from ltree import Ltree, Lquery


class BaseLtreeDumper(Dumper):
    def dump(self, obj: Ltree | Lquery) -> bytes:
        return str(obj).encode()


class BaseLtreeLoader(Loader):
    cls: type[Ltree] | type[Lquery]

    def load(self, buf: Buffer) -> Ltree | Lquery:
        return self.cls(bytes(buf).decode())


async def fetch_ltree_types(
    conn: AsyncConnection[Any],
) -> tuple[TypeInfo | None, TypeInfo | None]:
    t1 = await TypeInfo.fetch(conn, "ltree")
    t2 = await TypeInfo.fetch(conn, "lquery")
    return t1, t2


def register_ltree(
    ltree_info: TypeInfo, lquery_info: TypeInfo, context: AdaptContext | None = None
) -> None:
    """Register the adapters to load and dump ltree.

    :param ltree_info: The object with the information about the ltree type.
    :param lquery_info: The object with the information about the lquery type.
    :param context: The context where to register the adapters. If `!None`,
        register it globally.

    .. note::

        Registering the adapters doesn't affect objects already created, even
        if they are children of the registered context. For instance,
        registering the adapter globally doesn't affect already existing
        connections.
    """
    # A friendly error warning instead of an AttributeError in case fetch()
    # failed and it wasn't noticed.
    if not ltree_info or not lquery_info:
        raise TypeError("types info missing. Is the 'ltree' extension loaded?")

    # Register arrays and type info
    ltree_info.register(context)
    lquery_info.register(context)

    adapters = context.adapters if context else postgres.adapters

    # Generate and register a customized text dumper
    adapters.register_dumper(Ltree, _make_dumper(ltree_info.oid))
    adapters.register_dumper(Lquery, _make_dumper(lquery_info.oid))

    # register the text loader on the oid
    adapters.register_loader(ltree_info.oid, _make_loader(Ltree))
    adapters.register_loader(lquery_info.oid, _make_loader(Lquery))


# Cache all dynamically-generated types to avoid leaks in case the types
# cannot be GC'd.


@cache
def _make_dumper(oid_in: int) -> type[BaseLtreeDumper]:
    """
    Return a ltree/lquery dumper class configured using `oid_in`.

    Avoid to create new classes if the oid configured is the same.
    """

    class LtreeDumper(BaseLtreeDumper):
        oid = oid_in

    return LtreeDumper


@cache
def _make_loader(cls_in: type) -> type[BaseLtreeLoader]:
    """
    Return a ltree/lquery loader class configured using `type_in`.

    Avoid to create new classes if the oid configured is the same.
    """

    class LtreeLoader(BaseLtreeLoader):
        cls = cls_in

    return LtreeLoader
