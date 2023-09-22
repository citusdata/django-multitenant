from datetime import date
import re
import pytest
import django

from django.conf import settings
from django.db.models import Count
from django.db.utils import NotSupportedError, DataError
from .models import Store, Product, Purchase, Staff, StoreStaff


from django_multitenant.utils import (
    set_current_tenant,
    unset_current_tenant,
    get_current_tenant,
)

from .base import BaseTestCase


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
        from .models import SomeRelatedModel

        tenants = self.tenant_not_id

        self.assertEqual(SomeRelatedModel.objects.count(), 30)
        set_current_tenant(tenants[0])
        self.assertEqual(SomeRelatedModel.objects.count(), 10)
        unset_current_tenant()

    def test_select_tenant(self):
        from .models import Project

        # pylint: disable=pointless-statement
        self.projects
        project = Project.objects.first()

        # Selecting the account, account_id being tenant
        with self.assertNumQueries(1) as captured_queries:
            account = project.account
            self.assertTrue(
                f'"tests_account"."id" = {project.account_id}'
                in captured_queries.captured_queries[0]["sql"]
            )

    def test_select_tenant_not_id(self):
        # Test with tenant_id not id field

        from .models import SomeRelatedModel

        tenants = self.tenant_not_id
        some_related = SomeRelatedModel.objects.first()

        # Selecting the tenant, tenant_column being tenant_id in tests_tenantnodidmodel
        with self.assertNumQueries(1) as captured_queries:
            tenant = some_related.related_tenant
            self.assertTrue(
                f'"tests_tenantnotidmodel"."tenant_column" = {some_related.related_tenant_id}'
                in captured_queries.captured_queries[0]["sql"]
            )

    def test_select_tenant_foreign_key(self):
        from .models import Task

        # pylint: disable=pointless-statement
        self.tasks

        task = Task.objects.first()
        set_current_tenant(task.account)

        # Selecting task.project, account is tenant
        # To push down, account_id should be in query
        with self.assertNumQueries(1) as captured_queries:
            project = task.project
            self.assertTrue(
                f'AND "tests_project"."account_id" = {task.account_id}'
                in captured_queries.captured_queries[0]["sql"]
            )

        unset_current_tenant()

    def test_select_tenant_foreign_key_different_tenant_id(self):
        from .models import Revenue

        # pylint: disable=pointless-statement
        self.revenues

        revenue = Revenue.objects.first()
        set_current_tenant(revenue.acc)

        # Selecting revenue.project, project.account is tenant (revenue.acc is tenant)
        # To push down, account_id should be in query (not acc_id)
        with self.assertNumQueries(1) as captured_queries:
            project = revenue.project
            self.assertTrue(
                f'AND "tests_project"."account_id" = {revenue.acc_id}'
                in captured_queries.captured_queries[0]["sql"]
            )

        unset_current_tenant()

    def test_filter_select_related(self):
        from .models import Task

        task_id = self.tasks[0].pk

        # Test that the join clause has account_id
        with self.assertNumQueries(1) as captured_queries:
            task = Task.objects.filter(pk=task_id).select_related("project").first()

            self.assertEqual(task.account_id, task.project.account_id)
            pattern = (
                'INNER JOIN "tests_project" ON \\("tests_task"."project_id" = "tests_project"."id" AND'
                ' \\("tests_task"."account_id" = .?"tests_project"."account_id"\\)\\)'
            )
            self.assertTrue(
                bool(re.search(pattern, captured_queries.captured_queries[0]["sql"]))
            )

    def test_filter_select_related_not_id_field(self):
        from .models import SomeRelatedModel

        tenants = self.tenant_not_id
        some_related_id = SomeRelatedModel.objects.first().pk
        some_related_tenant_id = SomeRelatedModel.objects.first().related_tenant_id

        # Test that the join clause has account_id
        with self.assertNumQueries(1) as captured_queries:
            related = (
                SomeRelatedModel.objects.filter(pk=some_related_id)
                .select_related("related_tenant")
                .first()
            )

            self.assertEqual(related.related_tenant_id, some_related_tenant_id)
            self.assertTrue(
                'ON ("tests_somerelatedmodel"."related_tenant_id" = "tests_tenantnotidmodel"."tenant_column")'
                in captured_queries.captured_queries[0]["sql"]
            )

    def test_prefetch_related(self):
        from .models import Project

        project_managers = self.project_managers
        project_id = project_managers[0].project_id
        account = project_managers[0].account
        set_current_tenant(account)

        with self.assertNumQueries(2) as captured_queries:
            project = (
                Project.objects.filter(pk=project_id)
                .prefetch_related("managers")
                .first()
            )

            self.assertTrue(
                f'WHERE ("tests_manager"."account_id" = {project.account_id}'
                in captured_queries.captured_queries[1]["sql"]
            )
            pattern = 'AND \\("tests_projectmanager"."account_id" = .?"tests_manager"."account_id"\\)'
            self.assertTrue(
                bool(re.search(pattern, captured_queries.captured_queries[1]["sql"]))
            )

    def test_create_project(self):
        # Using save()

        from .models import Project

        account = self.account_fr

        project = Project()
        project.account = account
        project.name = "test save()"

        project.save()

        self.assertEqual(Project.objects.count(), 1)

    def test_create_project_tenant_set(self):
        # Using save()

        from .models import Project

        account = self.account_fr

        set_current_tenant(account)
        project = Project()
        project.name = "test save()"
        project.save()

        self.assertEqual(Project.objects.count(), 1)

        Project.objects.create(name="test create")
        self.assertEqual(Project.objects.count(), 2)

        unset_current_tenant()

    def test_bulk_create_tenant_set(self):
        from .models import Project

        account = self.account_fr

        set_current_tenant(account)
        projects = []
        for i in range(10):
            projects.append(Project(name=f"project {i}"))

        Project.objects.bulk_create(projects)

        unset_current_tenant()
        self.assertEqual(Project.objects.count(), 10)
        for project in Project.objects.all():
            self.assertEqual(project.account_id, account.id)

    def test_bulk_create_tenant_not_set(self):
        from .models import Project

        account = self.account_fr

        unset_current_tenant()
        projects = []
        for i in range(10):
            projects.append(Project(name=f"project {i}", account=account))

        Project.objects.bulk_create(projects)

        self.assertEqual(Project.objects.count(), 10)
        for project in Project.objects.all():
            self.assertEqual(project.account_id, account.id)

        projects = []
        for i in range(10):
            projects.append(Project(name=f"project {i}"))

        with self.assertRaises(DataError):
            Project.objects.bulk_create(projects)

    @pytest.mark.skipif(
        not settings.USE_CITUS,
        reason=(
            """ If table is distributed, we can't update the tenant column. 
                    If Citus is not enabled in settings, there is no reason to run this test."""
        ),
    )
    def test_update_tenant_project(self):
        from .models import Project

        account = self.account_fr

        project = Project()
        project.account = account
        project.name = "test save()"

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
        project.name = "test save()"
        project.save()

        self.assertEqual(Project.objects.count(), 1)

        project.account = account
        project.name = "test update"
        project.save()

        project = Project.objects.first()
        self.assertEqual(project.account, account)
        self.assertEqual(project.name, "test update")

    def test_delete_tenant_set(self):
        from .models import Project

        projects = self.projects
        account = self.account_fr

        self.assertEqual(Project.objects.count(), 30)

        set_current_tenant(account)
        query_count = 9 if django.VERSION >= (4, 2) else 7
        with self.assertNumQueries(query_count) as captured_queries:
            Project.objects.all().delete()
            unset_current_tenant()

            for query in captured_queries.captured_queries:
                print(f"SQL: {query['sql']}")

                if query["sql"] in ["BEGIN", "COMMIT"]:
                    continue
                if "tests_revenue" in query["sql"]:
                    self.assertTrue(f'"acc_id" = {account.id}' in query["sql"])
                else:
                    self.assertTrue(f'"account_id" = {account.id}' in query["sql"])

        self.assertEqual(Project.objects.count(), 20)

    def test_delete_tenant_not_set(self):
        from .models import Project

        projects = self.projects

        self.assertEqual(Project.objects.count(), 30)
        Project.objects.all().delete()
        self.assertEqual(Project.objects.count(), 0)

    def test_subquery(self):
        # we want all the projects with the name of their first task

        from django.db.models import OuterRef, Subquery
        from .models import Project, Task

        projects = self.projects
        account = self.account_fr
        tasks = self.tasks

        self.assertEqual(Project.objects.count(), 30)

        set_current_tenant(account)
        with self.assertNumQueries(1) as captured_queries:
            task_qs = Task.objects.filter(project=OuterRef("pk")).order_by("-name")
            projects = Project.objects.all().annotate(
                first_task_name=Subquery(task_qs.values("name")[:1])
            )
            for p in projects:
                self.assertTrue(p.first_task_name is not None)

            # check that tenant in subquery
            for query in captured_queries.captured_queries:
                self.assertTrue(f'U0."account_id" = {account.id}' in query["sql"])
                self.assertTrue(
                    f'WHERE "tests_project"."account_id" = {account.id}' in query["sql"]
                )

        unset_current_tenant()

    def test_subquery_joins(self):
        # we want all the projects with the name of their first task

        from django.db.models import OuterRef, Subquery
        from .models import Project, SubTask

        projects = self.projects
        account = self.account_fr
        subtasks = self.subtasks

        self.assertEqual(Project.objects.count(), 30)

        set_current_tenant(account)
        with self.assertNumQueries(1) as captured_queries:
            subtask_qs = SubTask.objects.filter(
                project=OuterRef("pk"), task__opened=True
            ).order_by("-name")
            projects = Project.objects.all().annotate(
                first_subtask_name=Subquery(subtask_qs.values("name")[:1])
            )
            for p in projects:
                self.assertTrue(p.first_subtask_name is not None)

            # check that tenant in subquery
            for query in captured_queries.captured_queries:
                self.assertTrue(f'U0."account_id" = {account.id}' in query["sql"])

                pattern = '\\(U0."task_id" = U\\d."id" AND \\(U0."account_id" = .?U\\d."account_id"\\)'
                self.assertTrue(bool(re.search(pattern, query["sql"])))
                self.assertTrue(
                    f'WHERE "tests_project"."account_id" = {account.id}' in query["sql"]
                )

        unset_current_tenant()

    def test_task_manager(self):
        from .models import Task

        projects = self.projects
        account = self.account_fr
        tasks = self.tasks

        set_current_tenant(account)

        self.assertEqual(len(Task.objects.closed()), 0)
        self.assertEqual(len(Task.objects.opened()), 50)

        task = Task.objects.first()
        task.opened = False
        task.save()

        self.assertEqual(len(Task.objects.closed()), 1)
        self.assertEqual(len(Task.objects.opened()), 49)

        unset_current_tenant()

    def test_str_model_tenant_set(self):
        projects = self.projects
        account = self.account_fr
        tasks = self.tasks

        set_current_tenant(account)

        unset_current_tenant()

    def test_str_model_tenant_not_set(self):
        projects = self.projects
        account = self.account_fr
        tasks = self.tasks

    def test_exclude_tenant_set(self):
        from .models import Task

        projects = self.projects
        account_fr = self.account_fr
        tasks = self.tasks

        unset_current_tenant()
        set_current_tenant(account_fr)

        tasks = Task.objects.exclude(project__isnull=True)

        self.assertEqual(tasks.count(), 50)

        unset_current_tenant()

    def test_exclude_tenant_not_set(self):
        from .models import Task

        projects = self.projects
        account_fr = self.account_fr
        tasks = self.tasks

        tasks = Task.objects.exclude(project__isnull=True)
        self.assertEqual(tasks.count(), 150)

    def test_delete_cascade_distributed(self):
        from .models import Task, Project, SubTask

        subtasks = self.subtasks
        account = self.account_fr

        unset_current_tenant()

        self.assertEqual(Project.objects.count(), 30)
        self.assertEqual(Task.objects.count(), 150)
        self.assertEqual(SubTask.objects.count(), 750)

        set_current_tenant(account)

        self.assertEqual(Project.objects.count(), 10)
        self.assertEqual(Task.objects.count(), 50)
        self.assertEqual(SubTask.objects.count(), 250)

        project = Project.objects.first()

        query_count = 14 if django.VERSION >= (4, 2) else 12

        with self.assertNumQueries(query_count) as captured_queries:
            project.delete()

            self.assertEqual(Project.objects.count(), 9)
            self.assertEqual(Task.objects.count(), 45)
            self.assertEqual(SubTask.objects.count(), 225)
            self.assertFalse(
                "SET LOCAL citus.multi_shard_modify_mode TO 'sequential';"
                in [query["sql"] for query in captured_queries.captured_queries]
            )
            self.assertFalse(
                "SET LOCAL citus.multi_shard_modify_mode TO 'parallel';"
                in [query["sql"] for query in captured_queries.captured_queries]
            )

    def test_delete_cascade_reference_to_distributed(self):
        from .models import Country, Account

        unset_current_tenant()

        country = self.france
        account1 = Account.objects.create(
            name="Account FR", country=country, subdomain="fr.", domain="citusdata.com"
        )

        account2 = Account.objects.create(
            name="Account FR 2", country=country, subdomain="fr.", domain="msft.com"
        )

        self.assertEqual(Account.objects.count(), 2)

        query_count = 18 if django.VERSION >= (4, 2) else 16
        with self.assertNumQueries(query_count) as captured_queries:
            country.delete()

            self.assertEqual(Account.objects.count(), 0)
            self.assertEqual(Country.objects.count(), 0)
            self.assertTrue(
                "SET LOCAL citus.multi_shard_modify_mode TO 'sequential';"
                in [query["sql"] for query in captured_queries.captured_queries]
            )
            self.assertTrue(
                "SET LOCAL citus.multi_shard_modify_mode TO 'parallel';"
                in [query["sql"] for query in captured_queries.captured_queries]
            )

    def test_delete_cascade_distributed_to_reference(self):
        from .models import Account, Employee, ModelConfig, Project

        unset_current_tenant()

        account = self.account_fr
        employee = Employee.objects.create(account=account, name="Louise")
        modelconfig = ModelConfig.objects.create(
            account=account, employee=employee, name="test"
        )
        projects = self.projects

        for project in projects:
            # pylint: disable=comparison-with-callable
            if project.account == account:
                project.employee = employee
                project.save(update_fields=["employee"])

        account.employee = employee
        account.save()

        self.assertEqual(Account.objects.count(), 3)
        self.assertEqual(Employee.objects.count(), 1)
        self.assertEqual(ModelConfig.objects.count(), 1)
        self.assertEqual(Project.objects.count(), 30)

        set_current_tenant(account)

        query_count = 29 if django.VERSION >= (4, 2) else 28
        with self.assertNumQueries(query_count) as captured_queries:
            account.delete()

            # Once deleted, we don't have a current tenant
            self.assertEqual(Account.objects.count(), 2)
            self.assertEqual(Employee.objects.count(), 0)
            self.assertEqual(ModelConfig.objects.count(), 0)
            self.assertEqual(Project.objects.count(), 20)
            self.assertTrue(
                "SET LOCAL citus.multi_shard_modify_mode TO 'sequential';"
                in [query["sql"] for query in captured_queries.captured_queries]
            )
            self.assertTrue(
                "SET LOCAL citus.multi_shard_modify_mode TO 'parallel';"
                in [query["sql"] for query in captured_queries.captured_queries]
            )

        unset_current_tenant()


class MultipleTenantModelTest(BaseTestCase):
    def test_filter_without_joins(self):
        from .models import Project, Account

        unset_current_tenant()
        projects = self.projects
        accounts = Account.objects.all().order_by("id")[1:]

        self.assertEqual(Project.objects.count(), 30)
        set_current_tenant(accounts)
        self.assertEqual(Project.objects.count(), 20)

        unset_current_tenant()

    def test_filter_without_joins_on_tenant_id_not_pk(self):
        from .models import SomeRelatedModel

        unset_current_tenant()
        tenants = self.tenant_not_id

        self.assertEqual(SomeRelatedModel.objects.count(), 30)
        set_current_tenant([tenants[0], tenants[1]])
        self.assertEqual(SomeRelatedModel.objects.count(), 20)

        unset_current_tenant()

    def test_select_tenant_foreign_key(self):
        from .models import Task, Account

        unset_current_tenant()
        # pylint: disable=pointless-statement
        self.tasks

        task = Task.objects.first()
        accounts = [task.account, Account.objects.last()]
        set_current_tenant(accounts)

        # Selecting task.project, account is tenant
        # To push down, account_id should be in query
        with self.assertNumQueries(1) as captured_queries:
            project = task.project
            self.assertTrue(
                f'AND "tests_project"."account_id" IN ({", ".join([str(account.id) for account in accounts])})'
                in captured_queries.captured_queries[0]["sql"]
            )

        unset_current_tenant()

    def test_select_tenant_foreign_key_different_tenant_id(self):
        from .models import Revenue, Account

        unset_current_tenant()
        # pylint: disable=pointless-statement
        self.revenues

        revenue = Revenue.objects.first()
        accounts = [revenue.acc, Account.objects.last()]
        set_current_tenant(accounts)

        # Selecting revenue.project, project.account is tenant (revenue.acc is tenant)
        # To push down, account_id should be in query (not acc_id)
        with self.assertNumQueries(1) as captured_queries:
            project = revenue.project
            self.assertTrue(
                f'AND "tests_project"."account_id" IN ({", ".join([str(account.id) for account in accounts])})'
                in captured_queries.captured_queries[0]["sql"]
            )

        unset_current_tenant()

    def test_prefetch_related(self):
        from .models import Project, Account

        unset_current_tenant()
        project_managers = self.project_managers
        project_id = project_managers[0].project_id
        accounts = [project_managers[0].account, Account.objects.last()]
        set_current_tenant(accounts)

        with self.assertNumQueries(2) as captured_queries:
            project = (
                Project.objects.filter(pk=project_id)
                .prefetch_related("managers")
                .first()
            )

            self.assertTrue(
                f'WHERE ("tests_manager"."account_id" IN ({", ".join([str(account.id) for account in accounts])})'
                in captured_queries.captured_queries[1]["sql"]
            )

            pattern = 'AND \\("tests_projectmanager"."account_id" = .?"tests_manager"."account_id"\\)'
            self.assertTrue(
                bool(re.search(pattern, captured_queries.captured_queries[1]["sql"]))
            )

        unset_current_tenant()

    def test_delete_tenant_set(self):
        from .models import Project, Account

        unset_current_tenant()
        projects = self.projects
        accounts = Account.objects.all().order_by("id")[1:]
        self.assertEqual(Project.objects.count(), 30)

        set_current_tenant(accounts)

        query_count = 10 if django.VERSION >= (4, 2) else 8
        with self.assertNumQueries(query_count) as captured_queries:
            Project.objects.all().delete()

            for query in captured_queries.captured_queries:
                if "tests_revenue" in query["sql"]:
                    self.assertTrue(
                        f'"acc_id" IN ({", ".join([str(account.id) for account in accounts])})'
                    )
                else:
                    self.assertTrue(
                        f'"account_id" IN ({", ".join([str(account.id) for account in accounts])})'
                    )

        unset_current_tenant()
        self.assertEqual(Project.objects.count(), 10)

    def test_subquery(self):
        # subquery don't work for multi tenants
        # we want all the projects with the name of their first task
        pass

    def test_uuid_create(self):
        from .models import Record

        organization = self.organization
        set_current_tenant(organization)
        record = Record.objects.create(name="record1")
        self.assertEqual(record.organization_id, organization.id)

    def test_uuid_save(self):
        from .models import Record

        organization = self.organization
        set_current_tenant(organization)
        record = Record(name="record1")
        record.save()

        record = Record.objects.first()
        self.assertEqual(record.organization_id, organization.id)

    def test_save_tenant_unset(self):
        unset_current_tenant()
        from .models import Project

        account = self.account_fr

        account_2 = self.account_us

        project = Project(account=account, name="test save fr")
        project.save()

        project2 = Project(account=account_2, name="test save us")
        project2.save()

        self.assertEqual(Project.objects.count(), 2)

        project.name = "test update name"
        project.save()

        project = Project.objects.first()
        self.assertEqual(project.name, "test update name")

    def test_save_tenant_set_different_than_object(self):
        unset_current_tenant()
        from .models import Project

        account = self.account_fr
        account_2 = self.account_us

        project = Project(account=account, name="test save fr")
        project.save()

        project2 = Project(account=account_2, name="test save us")
        project2.save()

        self.assertEqual(Project.objects.count(), 2)

        set_current_tenant(account_2)

        project.name = "test update name"
        project.save()

        current_tenant = get_current_tenant()
        self.assertEqual(current_tenant, account_2)

        unset_current_tenant()
        project = Project.objects.filter(account=account).first()
        self.assertEqual(project.name, "test update name")

    def test_save_tenant_set(self):
        unset_current_tenant()
        from .models import Project

        account = self.account_fr
        account_2 = self.account_us

        project = Project(account=account, name="test save fr")
        project.save()

        project2 = Project(account=account_2, name="test save us")
        project2.save()

        self.assertEqual(Project.objects.count(), 2)

        set_current_tenant(account)

        project.name = "test update name"
        project.save()

        current_tenant = get_current_tenant()
        self.assertEqual(current_tenant, account)

        unset_current_tenant()
        project = Project.objects.filter(account=account).first()
        self.assertEqual(project.name, "test update name")

    def test_aggregate(self):
        from .models import ProjectManager

        projects = self.projects
        managers = self.project_managers
        unset_current_tenant()
        projects_per_manager = ProjectManager.objects.annotate(Count("project_id"))
        list(projects_per_manager)

    def test_many_to_many_through_saves(self):
        store = Store.objects.create(name="store1")
        store.save()

        set_current_tenant(tenant=store)

        product = Product.objects.create(name="product1", store=store)
        product.save()

        purchase = Purchase.objects.create(store=store)
        purchase.save()
        purchase.product_purchased.add(product, through_defaults={"date": date.today()})

    def test_many_to_many_with_no_through_defaults_saves(self):
        store = Store.objects.create(name="store1")
        store.save()

        set_current_tenant(tenant=store)

        product = Product.objects.create(name="product1", store=store)
        product.save()

        purchase = Purchase.objects.create(store=store)
        purchase.save()
        purchase.product_purchased.add(product)

    def test_many_to_many_through_saves_to_nontenant(self):
        store = Store.objects.create(name="store1")
        store.save()

        set_current_tenant(tenant=store)

        staff = Staff.objects.create(name="staff1")

        store.store_staffs.add(staff)

        self.assertEqual(StoreStaff.objects.get(store=store, staff=staff).store, store)

    def test_tenant_id_columns(self):
        from .models import Template, Tenant, Business

        tenant = Tenant.objects.create(name="tenant")
        tenant.save()
        business = Business.objects.create(
            bk_biz_name="business", bk_biz_id=1, tenant=tenant
        )
        business.save()
        template = Template.objects.create(name="template", business=business)
        template.save()

        Template.objects.filter(business__tenant=tenant).first()
