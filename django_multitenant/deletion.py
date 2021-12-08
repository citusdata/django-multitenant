import operator
from functools import reduce

import django
from django.db.models import Q

from .utils import get_current_tenant, get_tenant_filters


def related_objects(obj, *args):
    if django.VERSION < (3, 0) or len(args) == 2:
        related = args[0]
        related_model = related.related_model
        related_fields = [related.field]
        objs = args[1]
    else:
        # Starting django 3.1 the signature of related_objects changed to
        # def related_objects(self, related_model, related_fields, objs)
        related_model = args[0]
        related_fields = args[1]
        objs = args[2]

    filters = {}
    predicate = reduce(
        operator.or_,
        (
            Q(**{"%s__in" % related_field.name: objs})
            for related_field in related_fields
        ),
    )

    if get_current_tenant():
        try:
            filters = get_tenant_filters(related_model)
        except ValueError:
            pass

    return related_model._base_manager.using(obj.using).filter(predicate, **filters)
