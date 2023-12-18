import sys
import importlib
from asgiref.sync import async_to_sync


from django_multitenant.utils import (
    set_current_tenant,
    get_current_tenant,
    unset_current_tenant,
    get_tenant_column,
    get_current_tenant_value,
    get_tenant_filters,
)

from .base import BaseTestCase


class UtilsTest(BaseTestCase):
    async def async_get_current_tenant(self):
        return get_current_tenant()

    async def async_set_current_tenant(self, tenant):
        return set_current_tenant(tenant)

    def test_set_current_tenant(self):
        projects = self.projects
        account = projects[0].account

        set_current_tenant(account)
        self.assertEqual(get_current_tenant(), account)
        unset_current_tenant()

    def test_tenant_persists_from_thread_to_async_task(self):
        projects = self.projects
        account = projects[0].account

        # Set the tenant in main thread
        set_current_tenant(account)

        with self.settings(TENANT_USE_ASGIREF=True):
            importlib.reload(sys.modules["django_multitenant.utils"])

            # Check the tenant within an async task when asgiref enabled
            tenant = async_to_sync(self.async_get_current_tenant)()
            self.assertEqual(get_current_tenant(), tenant)
            unset_current_tenant()

        with self.settings(TENANT_USE_ASGIREF=False):
            importlib.reload(sys.modules["django_multitenant.utils"])

            # Check the tenant within an async task when asgiref is disabled
            tenant = async_to_sync(self.async_get_current_tenant)()
            self.assertIsNone(get_current_tenant())
            unset_current_tenant()

    def test_tenant_persists_from_async_task_to_thread(self):
        projects = self.projects
        account = projects[0].account

        with self.settings(TENANT_USE_ASGIREF=True):
            importlib.reload(sys.modules["django_multitenant.settings"])
            importlib.reload(sys.modules["django_multitenant.utils"])

            # Set the tenant in task
            async_to_sync(self.async_set_current_tenant)(account)
            self.assertEqual(get_current_tenant(), account)
            unset_current_tenant()

        with self.settings(TENANT_USE_ASGIREF=False):
            importlib.reload(sys.modules["django_multitenant.settings"])
            importlib.reload(sys.modules["django_multitenant.utils"])

            # Set the tenant in task
            async_to_sync(self.async_set_current_tenant)(account)
            self.assertIsNone(get_current_tenant())
            unset_current_tenant()

    def test_get_tenant_column(self):
        from .models import Project

        projects = self.projects
        account = projects[0].account

        # test if instance
        column = get_tenant_column(account)
        self.assertEqual(column, "id")
        self.assertEqual(get_tenant_column(account), account.tenant_field)

        # test if  model
        column = get_tenant_column(Project)
        self.assertEqual(column, "account_id")

    def test_current_tenant_value_single(self):
        projects = self.projects
        account = projects[0].account
        set_current_tenant(account)

        self.assertEqual(get_current_tenant_value(), account.id)

        unset_current_tenant()

    def test_current_tenant_value_list(self):
        projects = self.projects
        accounts = [projects[0].account, projects[1].account]
        set_current_tenant(accounts)

        value = get_current_tenant_value()

        self.assertTrue(isinstance(value, list))
        self.assertEqual(value, [accounts[0].id, accounts[1].id])

        unset_current_tenant()

    def test_tenant_filters_single_tenant(self):
        from .models import Project

        projects = self.projects
        account = projects[0].account
        set_current_tenant(account)

        self.assertEqual(get_tenant_filters(Project), {"account_id": account.pk})

        unset_current_tenant()

    def test_tenant_filters_multi_tenant(self):
        from .models import Project

        projects = self.projects
        accounts = [projects[0].account, projects[1].account]
        set_current_tenant(accounts)

        self.assertEqual(
            get_tenant_filters(Project),
            {"account_id__in": [accounts[0].id, accounts[1].id]},
        )

        unset_current_tenant()

    def test_current_tenant_value_queryset_value(self):
        from .models import Account

        projects = self.projects
        accounts = Account.objects.all().order_by("id")
        set_current_tenant(accounts)

        value = get_current_tenant_value()

        self.assertTrue(isinstance(value, list))
        self.assertEqual(value, list(accounts.values_list("id", flat=True)))

        unset_current_tenant()

    def test_current_tenant_value_queryset_filter(self):
        from .models import Project, Account

        projects = self.projects
        accounts = Account.objects.all().order_by("id")
        set_current_tenant(accounts)

        value = get_current_tenant_value()

        self.assertEqual(
            get_tenant_filters(Project),
            {"account_id__in": list(accounts.values_list("id", flat=True))},
        )
        unset_current_tenant()
