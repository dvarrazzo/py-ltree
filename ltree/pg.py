from __future__ import annotations

from functools import cache

from psycopg import AsyncConnection, postgres
from psycopg.types import TypeInfo
from psycopg.abc import AdaptContext, Buffer
from psycopg.adapt import Dumper, Loader

from ltree import Ltree


class BaseLtreeDumper(Dumper):
    def dump(self, ltree: Ltree) -> bytes:
        return str(ltree).encode()


class LtreeLoader(Loader):
    def load(self, buf: Buffer) -> Ltree:
        return Ltree(bytes(buf).decode())


async def fetch_type(conn: AsyncConnection) -> TypeInfo | None:
    return await TypeInfo.fetch(conn, "ltree")


def register_ltree(info: TypeInfo, context: AdaptContext | None = None) -> None:
    """Register the adapters to load and dump ltree.

    :param info: The object with the information about the ltree type.
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
    if not info:
        raise TypeError("no info passed. Is the 'ltree' extension loaded?")

    # Register arrays and type info
    info.register(context)

    adapters = context.adapters if context else postgres.adapters

    # Generate and register a customized text dumper
    adapters.register_dumper(Ltree, _make_ltree_dumper(info.oid))

    # register the text loader on the oid
    adapters.register_loader(info.oid, LtreeLoader)


# Cache all dynamically-generated types to avoid leaks in case the types
# cannot be GC'd.


@cache
def _make_ltree_dumper(oid_in: int) -> type[BaseLtreeDumper]:
    """
    Return an hstore dumper class configured using `oid_in`.

    Avoid to create new classes if the oid configured is the same.
    """

    class LtreeDumper(BaseLtreeDumper):
        oid = oid_in

    return LtreeDumper
