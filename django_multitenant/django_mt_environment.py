import importlib


def import_drf_or_die():
    try:
        importlib.import_module("rest_framework")
    except ImportError as e:
        raise ImportError(
            "Django Multitenant requires Django Rest Framework to be installed."
        ) from e


import_drf_or_die()
