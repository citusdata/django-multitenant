from django_multitenant.utils import (set_current_tenant,
                                      get_current_tenant,
                                      unset_current_tenant)

from .base import BaseTestCase


class UtilsTest(BaseTestCase):
    def test_set_current_tenant(self):
        from .models import Project
        projects = self.projects
        account = projects[0].account

        set_current_tenant(account)
        self.assertEqual(get_current_tenant(), account)
        unset_current_tenant()

    def test_get_current_tenant(self):
        pass

    def test_get_tenant_column(self):
        pass

    def test_get_tenant_field(self):
        pass
