# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from .common import BaseRedmineTestCase


class TestRedmineConnector(BaseRedmineTestCase):
    def setUp(self):
        super(TestRedmineConnector, self).setUp()

    def test_01_redmine_mapper(self):
        with self.backend.work_on("redmine.account.analytic.line") as work:
            mapper_obj = work.component(usage="import.mapper")

            update = datetime(2015, 1, 1, 8, 32, 10)
            record = {"updated_on": update}

            self.assertEqual(
                mapper_obj.updated_on(record),
                {"updated_on": update.strftime(DEFAULT_SERVER_DATETIME_FORMAT)},
            )

            self.assertEqual(
                mapper_obj.backend_id(record), {"backend_id": self.backend.id}
            )

            now = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            self.assertEqual(mapper_obj.sync_date(record), {"sync_date": now})

    def test_02_redmine_binder_to_internal(self):
        with self.backend.work_on("redmine.account.analytic.line") as work:
            binder_obj = work.component(usage="binder")

            # Without the unwrap parameter, to_internal must return
            # the binding (redmine.account.analytic.line)
            binding = binder_obj.to_internal(123)

            self.assertEqual(binding.date, self.date_now)
            self.assertEqual(binding.redmine_id, 123)

            # With the unwrap parameter, to_internal must return
            # the ID of the odoo model record (account.analytic.line)
            timesheet = binder_obj.to_internal(123, unwrap=True)
            self.assertEqual(timesheet.date, self.date_now)

    def test_03_redmine_binder_to_external(self):
        with self.backend.work_on("redmine.account.analytic.line") as work:
            binder_obj = work.component(usage="binder")
            binding = self.redmine_timesheet
            timesheet = binding.odoo_id
            # Without the unwrap parameter, to_external must return
            # the external_id
            redmine_id = binder_obj.to_external(timesheet, wrap=True)
            redmine_id_2 = binder_obj.to_external(binding)

            self.assertEqual(redmine_id, redmine_id_2)
            self.assertEqual(redmine_id, 123)

    def test_04_redmine_binder_unwrap_binding(self):
        """If the object is already a binding then unwrap_binding should return
        it. Otherwise it should browse it."""

        with self.backend.work_on("redmine.account.analytic.line") as work:
            binder_obj = work.component(usage="binder")
            binding = self.redmine_timesheet

            timesheet = binder_obj.unwrap_binding(binding)
            self.assertEqual(timesheet.date, self.date_now)

            timesheet_2 = binder_obj.unwrap_binding(binding.id)
            self.assertEqual(timesheet, timesheet_2)

    def test_05_redmine_binder_unwrap_model(self):
        with self.backend.work_on("redmine.account.analytic.line") as work:
            binder_obj = work.component(usage="binder")
            self.assertEqual(binder_obj.unwrap_model(), "account.analytic.line")

    # TODO: Enable when importing time entry

    def test_06_import_synchronizer_get_binding_id(self):
        with self.backend.work_on("redmine.account.analytic.line") as work:
            synchronizer = work.component(usage="record.importer")

            binding = self.redmine_model.search([("redmine_id", "=", 123)])[0]

            synchronizer.redmine_id = 123
            self.assertEqual(synchronizer._get_binding(), binding)

    def test_07_import_synchronizer_update(self):
        with self.backend.work_on("redmine.account.analytic.line") as work:
            synchronizer = work.component(usage="record.importer")

            synchronizer.redmine_id = 123

            new_vals = {
                "name": "New Name",
                "unit_amount": 10,
            }
            synchronizer._update(synchronizer._get_binding(), new_vals)

            for val in new_vals:
                self.assertEqual(new_vals[val], self.redmine_timesheet[val])

    def test_08_import_synchronizer_create(self):
        with self.backend.work_on("redmine.account.analytic.line") as work:
            synchronizer = work.component(usage="record.importer")
            synchronizer.redmine_id = 345

            vals = self.timesheet_vals
            vals["redmine_id"] = 345
            vals["name"] = "Second Timesheet"

            binding = synchronizer._create(vals)

            self.assertEqual(binding.name, vals["name"])
