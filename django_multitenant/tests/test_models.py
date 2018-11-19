from django_multitenant.utils import set_current_tenant

from .base import BaseTestCase
# from .models import Project, Account



class TenantModelTest(BaseTestCase):
    def test_filter_without_joins(self):
        from .models import Project
        projects = self.projects
        account = self.account_fr

        self.assertEqual(Project.objects.count(), len(projects))
        set_current_tenant(account)
        self.assertEqual(Project.objects.count(), account.projects.count())
