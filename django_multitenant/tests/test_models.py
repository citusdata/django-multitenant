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

    def test_select_tenant(self):
        from .models import Project
        self.projects
        project = Project.objects.first()

        # Selecting the account, account_id being tenant
        with self.assertNumQueries(1) as captured_queries:
            account = project.account
            self.assertTrue('"tests_account"."id" = %d' % project.account_id \
                            in captured_queries.captured_queries[0]['sql'])


    def test_select_tenant_foreign_key(self):
        from .models import Task
        self.tasks

        task = Task.objects.first()

        # Selecting task.project, account is tenant
        # To push down, account_id should be in query
        with self.assertNumQueries(1) as captured_queries:
            project = task.project
            self.assertTrue('AND "tests_project"."account_id" = %d' % task.account_id \
                            in captured_queries.captured_queries[0]['sql'])


    def test_filter_select_related(self):
        from .models import Task
        task_id = self.tasks[0].pk

        # Test that the join clause has account_id
        with self.assertNumQueries(1) as captured_queries:
            task = Task.objects.filter(pk=task_id).select_related('project').first()

            self.assertEqual(task.account_id, task.project.account_id)
            self.assertTrue('INNER JOIN "tests_project" ON ("tests_task"."project_id" = "tests_project"."id" AND ("tests_task"."account_id" = ("tests_project"."account_id")))' \
                            in captured_queries.captured_queries[0]['sql'])


    def test_prefetch_related(self):
        from .models import Project

        project_managers = self.project_managers
        project_id = project_managers[0].project_id

        with self.assertNumQueries(2) as captured_queries:
            project = Project.objects.filter(pk=project_id).prefetch_related('managers').first()

            self.assertTrue('WHERE ("tests_manager"."account_id" = %d' % project.account_id \
                            in captured_queries.captured_queries[1]['sql'])
            self.assertTrue('AND ("tests_projectmanager"."account_id" = ("tests_manager"."account_id"))' \
                            in captured_queries.captured_queries[1]['sql'])
