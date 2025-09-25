from __future__ import annotations

from typing import Any
from functools import cache

import psycopg.errors as e
from psycopg import AsyncConnection, postgres
from psycopg.pq import Format
from psycopg.abc import AdaptContext, Buffer
from psycopg.adapt import Dumper, Loader
from psycopg.types import TypeInfo

from ltree import Ltree, Lquery


class BaseLtreeDumper(Dumper):
    def dump(self, obj: Ltree | Lquery) -> bytes:
        return str(obj).encode()


class BaseLtreeBinaryDumper(BaseLtreeDumper):
    format: Format = Format.BINARY

    def dump(self, obj: Ltree | Lquery) -> bytes:
        return b"\01" + super().dump(obj)


class BaseLtreeLoader(Loader):
    cls: type[Ltree] | type[Lquery]

    def load(self, buf: Buffer) -> Ltree | Lquery:
        return self.cls(bytes(buf).decode())


class BaseLtreeBinaryLoader(BaseLtreeLoader):
    format: Format = Format.BINARY

    def load(self, buf: Buffer) -> Ltree | Lquery:
        if not buf:
            raise e.DataError(f"empty buffer in {type(self).__name__}")

        if buf[0] != 1:
            raise e.NotSupportedError(f"unknown Ltree/Lquery version: {buf[0]}")

        return super().load(buf[1:])


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

    for oid, typ in [(ltree_info.oid, Ltree), (lquery_info.oid, Lquery)]:
        base: type
        for base in BaseLtreeDumper, BaseLtreeBinaryDumper:
            adapters.register_dumper(typ, _make_dumper(oid, base))

        for base in BaseLtreeLoader, BaseLtreeBinaryLoader:
            adapters.register_loader(oid, _make_loader(typ, base))


# Cache all dynamically-generated types to avoid leaks in case the types
# cannot be GC'd.


@cache
def _make_dumper(oid_in: int, base: type[BaseLtreeDumper]) -> type[BaseLtreeDumper]:
    """
    Return a ltree/lquery dumper class configured using `oid_in`.

    Avoid to create new classes if the oid configured is the same.
    """
    return type(base.__name__.replace("Base", ""), (base,), {"oid": oid_in})


@cache
def _make_loader(cls_in: type, base: type[BaseLtreeLoader]) -> type[BaseLtreeLoader]:
    """
    Return a ltree/lquery loader class configured using `type_in`.

    Avoid to create new classes if the oid configured is the same.
    """
    return type(base.__name__.replace("Base", ""), (base,), {"cls": cls_in})
