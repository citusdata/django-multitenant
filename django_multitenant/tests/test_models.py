from django.db.utils import NotSupportedError
from django_multitenant.utils import set_current_tenant, unset_current_tenant

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
        unset_current_tenant()


    def test_filter_without_joins_on_tenant_id_not_pk(self):
        from .models import TenantNotIdModel, SomeRelatedModel
        tenants = self.tenant_not_id

        self.assertEqual(SomeRelatedModel.objects.count(), 30)
        set_current_tenant(tenants[0])
        self.assertEqual(SomeRelatedModel.objects.count(), 10)
        unset_current_tenant()

    def test_select_tenant(self):
        from .models import Project
        self.projects
        project = Project.objects.first()

        # Selecting the account, account_id being tenant
        with self.assertNumQueries(1) as captured_queries:
            account = project.account
            self.assertTrue('"tests_account"."id" = %d' % project.account_id \
                            in captured_queries.captured_queries[0]['sql'])


    def test_select_tenant_not_id(self):
        # Test with tenant_id not id field
        from .models import SomeRelatedModel

        tenants = self.tenant_not_id
        some_related = SomeRelatedModel.objects.first()

        # Selecting the tenant, tenant_column being tenant_id in tests_tenantnodidmodel
        with self.assertNumQueries(1) as captured_queries:
            tenant = some_related.related_tenant
            self.assertTrue('"tests_tenantnotidmodel"."tenant_column" = %d' % some_related.related_tenant_id \
                            in captured_queries.captured_queries[0]['sql'])

    def test_select_tenant_foreign_key(self):
        from .models import Task
        self.tasks

        task = Task.objects.first()
        set_current_tenant(task.account)

        # Selecting task.project, account is tenant
        # To push down, account_id should be in query
        with self.assertNumQueries(1) as captured_queries:
            project = task.project
            self.assertTrue('AND "tests_project"."account_id" = %d' % task.account_id \
                            in captured_queries.captured_queries[0]['sql'])


        unset_current_tenant()

    def test_filter_select_related(self):
        from .models import Task
        task_id = self.tasks[0].pk

        # Test that the join clause has account_id
        with self.assertNumQueries(1) as captured_queries:
            task = Task.objects.filter(pk=task_id).select_related('project').first()

            self.assertEqual(task.account_id, task.project.account_id)
            self.assertTrue('INNER JOIN "tests_project" ON ("tests_task"."project_id" = "tests_project"."id" AND ("tests_task"."account_id" = ("tests_project"."account_id")))' \
                            in captured_queries.captured_queries[0]['sql'])


    def test_filter_select_related_not_id_field(self):
        from .models import SomeRelatedModel
        tenants = self.tenant_not_id
        some_related_id = SomeRelatedModel.objects.first().pk
        some_related_tenant_id = SomeRelatedModel.objects.first().related_tenant_id

        # Test that the join clause has account_id
        with self.assertNumQueries(1) as captured_queries:
            related = SomeRelatedModel.objects.filter(pk=some_related_id).select_related('related_tenant').first()

            self.assertEqual(related.related_tenant_id, some_related_tenant_id)
            self.assertTrue('ON ("tests_somerelatedmodel"."related_tenant_id" = "tests_tenantnotidmodel"."tenant_column")' \
                            in captured_queries.captured_queries[0]['sql'])


    def test_prefetch_related(self):
        from .models import Project

        project_managers = self.project_managers
        project_id = project_managers[0].project_id
        account = project_managers[0].account
        set_current_tenant(account)

        with self.assertNumQueries(2) as captured_queries:
            project = Project.objects.filter(pk=project_id).prefetch_related('managers').first()

            self.assertTrue('WHERE ("tests_manager"."account_id" = %d' % project.account_id \
                            in captured_queries.captured_queries[1]['sql'])
            self.assertTrue('AND ("tests_projectmanager"."account_id" = ("tests_manager"."account_id"))' \
                            in captured_queries.captured_queries[1]['sql'])

    def test_create_project(self):
        # Using save()
        from .models import Project
        account = self.account_fr

        project = Project()
        project.account = account
        project.name = 'test save()'

        project.save()

        self.assertEqual(Project.objects.count(), 1)

    def test_update_tenant_project(self):
        from .models import Project
        account = self.account_fr

        project = Project()
        project.account = account
        project.name = 'test save()'

        project.save()

        self.assertEqual(Project.objects.count(), 1)

        project.account = self.account_in

        with self.assertRaises(NotSupportedError):
            project.save()

        project = Project.objects.first()
        self.assertEqual(project.account, account)

    def test_save_project(self):
        from .models import Project
        account = self.account_fr

        project = Project()
        project.account = account
        project.name = 'test save()'
        project.save()

        self.assertEqual(Project.objects.count(), 1)

        project.account = account
        project.name = 'test update'
        project.save()

        project = Project.objects.first()
        self.assertEqual(project.account, account)
        self.assertEqual(project.name, 'test update')

    def test_delete_tenant_set(self):
        from .models import Project
        projects = self.projects
        account = self.account_fr

        self.assertEqual(Project.objects.count(), 30)

        set_current_tenant(account)
        with self.assertNumQueries(6) as captured_queries:
            Project.objects.all().delete()
            unset_current_tenant()

            for query in captured_queries.captured_queries:
                self.assertTrue('"account_id" = %d' % account.id in query['sql'])

        self.assertEqual(Project.objects.count(), 20)

    def test_delete_tenant_not_set(self):
        from .models import Project
        projects = self.projects

        self.assertEqual(Project.objects.count(), 30)
        Project.objects.all().delete()
        self.assertEqual(Project.objects.count(), 0)
