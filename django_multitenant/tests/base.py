from django.db import connection
from django.test import TestCase, TransactionTestCase

from exam.cases import Exam
from exam.decorators import fixture, before, after

from .models import *


class Fixtures(Exam):
    # @after
    # def print_after(self):
    #     for q in connection.queries:
    #         print(q['sql'])

    @fixture
    def india(self):
        return Country.objects.create(name='India')

    @fixture
    def france(self):
        return Country.objects.create(name='France')

    @fixture
    def united_states(self):
        return Country.objects.create(name='United States')

    @fixture
    def account_fr(self):
        return Account.objects.create(pk=1,
                                      name='Account FR',
                                      country=self.france,
                                      subdomain='fr.',
                                      domain='citusdata.com')

    @fixture
    def account_in(self):
        return Account.objects.create(pk=2,
                                      name='Account IN',
                                      country=self.india,
                                      subdomain='in.',
                                      domain='citusdata.com')

    @fixture
    def account_us(self):
        return Account.objects.create(pk=3,
                                      name='Account US',
                                      country=self.united_states,
                                      subdomain='us.',
                                      domain='citusdata.com')


    @fixture
    def accounts(self):
        return [self.account_fr, self.account_in, self.account_us]


    @fixture
    def projects(self):
        projects = []

        for account in self.accounts:
            for i in range(10):
                projects.append(
                    Project.objects.create(account_id=account.pk,
                                           name='project %d' % i)
                )

        return projects


    @fixture
    def managers(self):
        managers = []

        for account in self.accounts:
            for i in range(5):
                managers.append(
                    Manager.objects.create(name='manager %d' % i,
                                           account=account)
                )

        return managers

    @fixture
    def tasks(self):
        tasks = []

        for project in self.projects:
            previous_task = None
            for i in range(5):
                previous_task = Task.objects.create(
                    name='task project %s %i' %(project.name, i),
                    project_id=project.pk,
                    account_id=project.account_id,
                    parent=previous_task)

                tasks.append(previous_task)

        return tasks

    @fixture
    def revenues(self):
        revenues = []

        for project in self.projects:
            for i in range(5):
                revenue = Revenue.objects.create(
                    value="%s mil" % i,
                    project_id=project.pk,
                    acc_id=project.account_id,
                )
                revenues.append(revenue)

        return revenues

    @fixture
    def project_managers(self):
        projects = self.projects
        managers = self.managers
        project_managers = []

        for project in projects:
            for manager in project.account.managers.all():
                project_managers.append(
                    ProjectManager.objects.create(account=project.account,
                                                  project=project,
                                                  manager=manager))
        return project_managers

    @fixture
    def subtasks(self):
        subtasks = []

        for task in self.tasks:
            for i in range(5):
                subtasks.append(
                    SubTask.objects.create(
                        name='subtask project %i, task %i',
                        type='test',
                        account_id=task.account_id,
                        project_id=task.project_id,
                        task=task)
                )

        return subtasks

    @fixture
    def unscoped(self):
        pass

    @fixture
    def aliased_tasks(self):
        pass

    @fixture
    def organization(self):
        return Organization.objects.create(name='organization')

    @fixture
    def tenant_not_id(self):
        tenants = []
        for i in range(3):
            tenant = TenantNotIdModel(tenant_column=i+1,
                                      name='test %d' % i)
            tenant.save()

            tenants.append(tenant)

            for j in range(10):
                SomeRelatedModel.objects.create(related_tenant=tenant,
                                                name='related %d' % j)
        return tenants


class BaseTestCase(Fixtures, TransactionTestCase):
    pass
