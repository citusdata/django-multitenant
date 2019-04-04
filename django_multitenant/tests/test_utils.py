from django_multitenant.utils import (set_current_tenant,
                                      get_current_tenant,
                                      unset_current_tenant,
                                      get_tenant_column,
                                      get_current_tenant_value,
                                      get_tenant_filters)

from .base import BaseTestCase


class UtilsTest(BaseTestCase):
    def test_set_current_tenant(self):
        from .models import Project
        projects = self.projects
        account = projects[0].account

        set_current_tenant(account)
        self.assertEqual(get_current_tenant(), account)
        unset_current_tenant()

    def test_get_tenant_column(self):
        from .models import Project
        projects = self.projects
        account = projects[0].account

        # test if instance
        column = get_tenant_column(account)
        self.assertEqual(column, 'id')
        self.assertEqual(get_tenant_column(account), account.tenant_field)

        # test if  model
        column = get_tenant_column(Project)
        self.assertEqual(column, 'account_id')

    def test_current_tenant_value_single(self):
        from .models import Project, Account

        projects = self.projects
        account = projects[0].account
        set_current_tenant(account)

        self.assertEqual(get_current_tenant_value(), account.id)

        unset_current_tenant()

    def test_current_tenant_value_list(self):
        from .models import Project, Account

        projects = self.projects
        accounts = [projects[0].account, projects[1].account]
        set_current_tenant(accounts)

        value = get_current_tenant_value()

        self.assertTrue(isinstance(value, list))
        self.assertEqual(value, [accounts[0].id, accounts[1].id])

        unset_current_tenant()

    def test_current_tenant_value_queryset(self):
        from .models import Project, Account

        projects = self.projects
        accounts = Account.objects.all().order_by('id')
        set_current_tenant(accounts)

        value = get_current_tenant_value()

        self.assertTrue(isinstance(value, list))
        self.assertEqual(value, accounts.values_list('id', flat=True))

        unset_current_tenant()

    def test_tenant_filters_single_tenant(self):
        from .models import Project, Account

        projects = self.projects
        account = projects[0].account
        set_current_tenant(account)

        self.assertEqual(get_tenant_filters(Project), {'account_id': account.pk})

        unset_current_tenant()

    def test_tenant_filters_multi_tenant(self):
        from .models import Project, Account

        projects = self.projects
        accounts = [projects[0].account, projects[1].account]
        set_current_tenant(accounts)

        self.assertEqual(get_tenant_filters(Project),
                         {'account_id__in': [accounts[0].id, accounts[1].id]})

        unset_current_tenant()

    def test_current_tenant_value_queryset(self):
        from .models import Project, Account

        projects = self.projects
        accounts = Account.objects.all().order_by('id')
        set_current_tenant(accounts)

        value = get_current_tenant_value()

        self.assertEqual(get_tenant_filters(Project),
                         {'account_id__in': list(accounts.values_list('id', flat=True))})
        unset_current_tenant()
