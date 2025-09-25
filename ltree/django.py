from __future__ import absolute_import

from django.db.models import Lookup
from django.db.models.fields import Field


@Field.register_lookup
class LqueryMatch(Lookup):  # type: ignore[misc]
    lookup_name = "lqmatch"

    def as_postgresql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return "%s ~ %s" % (lhs, rhs), params

    def as_sql(self, compiler, connection):
        raise NotImplementedError(
            "database vendor %s doesn't support Lquery" % connection.vendor
        )
