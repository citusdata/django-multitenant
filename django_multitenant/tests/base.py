from django.test import TestCase

from exam.cases import Exam
from exam.decorators import fixture, before, after


class Fixtures(Exam):
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
        return Account.objects.create(name='Account FR',
                                      country=self.france,
                                      subdomain='fr.',
                                      domain='citusdata.com')

    @fixture
    def account_in(self):
        return Account.objects.create(name='Account IN',
                                      country=self.india,
                                      subdomain='in.',
                                      domain='citusdata.com')

    @fixture
    def account_us(self):
        return Account.objects.create(name='Account US',
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
                    Project.objects.create(account=account,
                                           name='project %d' % i)
                )

        return projects


    @fixture
    def managers(self):
        managers = []

        for account in self.accounts:
            for i in range(5):
                managers.append(
                    Manager.objects.create(name='manager %d' % i)
                )

        return managers

    @fixture
    def tasks(self):
        tasks = []

        for project in self.projects:
            for i in range(5):
                tasks.append(
                    Task.objects.create(
                        name='task project %s %i' %(project.name, i),
                        project=project,
                        account=project.account))

        return tasks

    @fixture
    def subtasks(self):
        pass

    @fixture
    def unscoped(self):
        pass

    @fixture
    def aliased_tasks(self):
        pass

    @fixture
    def organizations(self):
        pass

    @fixture
    def records(self):
        pass


class BaseTestCase(Fixtures, TestCase):
    pass
