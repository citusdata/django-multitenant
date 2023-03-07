import importlib


def check_drf():
    try:
        importlib.import_module("rest_framework")
    except ImportError as e:
        raise ImportError(
            "Django Multitenant requires Django Rest Framework to be installed."
        ) from e


check_drf()
