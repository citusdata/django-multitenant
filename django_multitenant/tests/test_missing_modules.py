from django.test import TransactionTestCase
import pytest
import importlib


class ModuleImportTestCases(TransactionTestCase):
    def test_missing_drf(self):
        with pytest.raises(
            ImportError,
            match="Django Multitenant requires Django Rest Framework to be installed.",
        ):
            importlib.import_module("django_multitenant.views")
