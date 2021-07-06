# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import namedtuple
from datetime import datetime

from odoo.addons.component.tests.common import TransactionComponentCase

Issue = namedtuple("Issue", "id subject")

Activity = namedtuple("Activity", "id name")

TimeEntry = namedtuple(
    "TimeEntry", "issue_id issue spent_on hours activity activity_id comments"
)


class BaseRedmineTestCase(TransactionComponentCase):
    def setUp(self):
        super(BaseRedmineTestCase, self).setUp()
        self.backend_model = self.env["redmine.backend"]
        self.user_model = self.env["res.users"]
        self.employee_model = self.env["hr.employee"]
        self.timesheet_model = self.env["account.analytic.line"]
        self.account_model = self.env["account.analytic.account"]
        self.general_account_model = self.env["account.account"]
        self.product_model = self.env["product.product"]
        self.redmine_model = self.env["redmine.account.analytic.line"]
        self.project_model = self.env["project.project"]
        self.task_model = self.env["project.task"]
        self.issue_model = self.env["redmine.issue"]

        self.user_1 = self.user_model.create(
            {
                "name": "User 1",
                "login": "user_1",
            }
        )

        self.project = self.project_model.create(
            {
                "name": "Project_1",
                "allow_timesheets": True,
                "privacy_visibility": "employees",
                "redmine_project_url": "http://localhost:3000/projects/project1",
            }
        )
        self.task = self.task_model.create(
            {
                "name": "Task One",
                "priority": "0",
                "kanban_state": "normal",
                "project_id": self.project.id,
            }
        )
        self.account = self.project.analytic_account_id

        self.project_2 = self.project_model.create(
            {
                "name": "Project_2",
                "allow_timesheets": True,
                "privacy_visibility": "employees",
                "redmine_project_url": "http://localhost:3000/projects/project2",
            }
        )

        self.account_2 = self.project_2.analytic_account_id

        self.product = self.product_model.search([("type", "=", "service")])[0]

        self.general_account = self.general_account_model.create(
            {
                # 'type': 'other',
                "code": "123123",
                "name": "test",
                # 'user_type': self.ref('account.data_account_type_expense'),
                "user_type_id": self.ref("account.data_account_type_expenses"),
            }
        )

        self.product.write(
            {
                "property_account_expense_id": self.general_account.id,
            }
        )

        self.employee = self.employee_model.create(
            {
                "name": "Employee 1",
                "user_id": self.user_1.id,
                # 'journal_id': journal.id,
                # 'product_id': self.product.id,
            }
        )

        self.backend = self.backend_model.create(
            {
                "name": "redmine_test",
                "location": self.project.redmine_project_url,
                "key": "39730056c1df6fb97b4fa5b9eb4bd37221ca1223",
                "version": "1.3",
                "contract_ref": "abcd",
                # "location": "http://localhost:3000/",
            }
        )


        self.now = datetime.now()
        self.date_now = datetime.now().date()

        self.issue = self.issue_model.create(
            {
                "name": "Redmine issue",
                "odoo_id": self.task.id,
                "backend_id": self.backend.id,
                "redmine_id": 123,
                "sync_date": self.now,
            }
        )

        self.timesheet_vals = {
            "redmine_id": 123,
            "updated_on": self.now,
            "backend_id": self.backend.id,
            "sync_date": self.now,
            "user_id": self.user_1.id,
            "date": self.date_now,
            "account_id": self.account.id,
            # 'account_id': self.project.analytic_account_id.id,
            # 'task_id': ,
            "issue_id": self.issue.id,
            "employee_id": self.employee.id,
            "unit_amount": 5,
            "name": "Test",
        }

        self.redmine_timesheet = self.redmine_model.create(self.timesheet_vals)
