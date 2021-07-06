# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from .common import Activity, BaseRedmineTestCase, Issue, TimeEntry

# from mock import patch
# from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


import_job_path = (
    "odoo.addons.connector_redmine.unit.import_synchronizer." "import_record.delay"
)


def mock_delay(model_name, *args, **kwargs):
    """Enqueue the function. Return the uuid of the created job."""
    return import_record(model_name, *args, **kwargs)


class TestImportIssues(BaseRedmineTestCase):
    def setUp(self):
        super(TestImportIssues, self).setUp()
        self.project_model = self.env["project.project"]
        self.task_model = self.env["project.task"]
        self.issue_model = self.env["redmine.issue"]

    def get_time_entry_defaults(self):
        issue = Issue(
            id=self.issue.redmine_id,
            subject=self.issue.name,
        )
        activity = Activity(
            id=100,
            name="test Activity 1",
        )
        time_entry = TimeEntry(
            issue_id=issue.id,
            issue=issue,
            activity_id=activity.id,
            activity=activity,
            hours=8.5,
            spent_on="2015-01-01",
            comments="Test Mapping of Time Entry",
        )
        res = {
            "contract_ref": self.project.name,
            "updated_on": datetime(2015, 4, 8, 20, 38, 31),
            "time_entry": time_entry,
            "user_login": "user_1",
            "redmine_id": 123,
        }
        return res

    def test_01_mapper_analytic_account(self):
        """
        Test that the proper analytic account is mapped
        """
        with self.backend.work_on("redmine.account.analytic.line") as work:
            mapper_obj = work.component(usage="import.mapper")

            defaults = self.get_time_entry_defaults()
            map_record = mapper_obj.map_record(defaults)
            res = map_record.values(for_create=True)

            self.assertEqual(res["account_id"], self.account.id)

            defaults["contract_ref"] = "Project_2"
            map_record = mapper_obj.map_record(defaults)
            res = map_record.values()

            self.assertEqual(res["account_id"], self.account_2.id)

    def test_02_binder(self):
        with self.backend.work_on("redmine.account.analytic.line") as work:
            binder = work.component(usage="binder")
            mapper_obj = work.component(usage="import.mapper")

            defaults = self.get_time_entry_defaults()
            map_record = mapper_obj.map_record(defaults)
            data = map_record.values(for_create=True)
            binding_id = self.env["redmine.account.analytic.line"].create(data).id

            binder.bind(123, binding_id)

    # TODO: Implement the following tests according to the last changes
    #       in the port

    # @patch(import_job_path, side_effect=mock_delay)
    # def import_time_entry_batch(
    #     self, record_id, defaults, job_decorator, options=None
    # ):
    #     adapter = backend_adapter.TimeEntryAdapter
    #     with patch.object(adapter, 'read') as read, \
    #             patch.object(adapter, 'search') as search:

    #         search.return_value = [record_id]
    #         read.return_value = defaults

    #         import_batch(
    #             'redmine.account.analytic.line',
    #             self.backend, filters={
    #                 'from_date': '2015-01-01',
    #                 'to_date': '2015-01-07',
    #             }, options=options)

    # def test_03_import_batch_synchronizer(self):
    #     defaults = self.get_time_entry_defaults()
    #     self.import_time_entry_batch(123, defaults)

    #     timesheet = self.redmine_model.search([('redmine_id', '=', 123)])[0]

    #     self.assertEqual(timesheet.account_id, self.account)
    #     self.assertEqual(timesheet.unit_amount, 8.5)
    #     self.assertEqual(timesheet.date, '2015-01-01')
    #     self.assertEqual(timesheet.user_id, self.user_1)
    #     self.assertEqual(timesheet.product_id.id, self.product.id)
    #     self.assertEqual(timesheet.amount, -8.5 * 30)

    #     defaults['contract_ref'] = 'efgh'
    #     defaults['hours'] = 10
    #     defaults['spent_on'] = '2015-01-02'
    #     self.import_time_entry_batch(123, defaults)

    #     self.backend.refresh()
    #     self.assertEqual(
    #         self.backend.time_entry_last_update,
    #         datetime(2015, 4, 8, 20, 38, 31).strftime(
    #             DEFAULT_SERVER_DATETIME_FORMAT))

    #     timesheet.refresh()
    #     self.assertEqual(timesheet.account_id, self.account_2)
    #     self.assertEqual(timesheet.unit_amount, 10)
    #     self.assertEqual(timesheet.date, '2015-01-02')

    # def test_04_cron_job(self):
    #     """
    #     Test that the import cron job executes without error
    #     """
    #     self.backend_model.prepare_time_entry_import()

    # def test_05_import_single_user_time_entries_mapping_error(self):
    #     with self.backend.work_on('redmine.account.analytic.line') as work:
    #         adapter = work.component(usage='backend.adapter')
    #         with patch.object(adapter, 'search_user') as search_user, \
    #                 patch.object(adapter, 'read') as read, \
    #                 patch.object(adapter, 'search') as search:

    #             defaults = self.get_time_entry_defaults()

    #             updated_on = self.project.last_imported_on

    #             search_user.return_value = 1
    #             search.return_value = [1, 2]

    #             def side_effect(redmine_id):
    #                 if redmine_id == 1:
    #                     return defaults
    #                 return dict(defaults, contract_ref='not mapped')

    #             read.side_effect = side_effect

    #             self.project.import_issues_from_redmine()

    #             # Time entry 1 is mapped, but entry 2 is not mapped.
    #             # So one is created and the other is logged in the chatter.
    #             self.assertEqual(len(timesheet.timesheet_ids), 1)

    #             entry = timesheet.timesheet_ids[0]
    #             self.assertEqual(entry.to_invoice.id, self.ref(
    #                 'hr_timesheet_invoice.timesheet_invoice_factor2'))

    #             self.backend.refresh()

    #             # Backend field time_entry_last_update must not be updated when
    #             # querying timesheets for a single user
    #             self.assertEqual(updated_on, self.project.last_imported_on)
