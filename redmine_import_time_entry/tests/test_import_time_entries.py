# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

from openerp.addons.connector.connector import ConnectorEnvironment

from openerp.addons.connector_redmine.session import RedmineConnectorSession
from openerp.addons.connector_redmine.unit.binder import RedmineModelBinder
from openerp.addons.connector_redmine.unit.import_synchronizer import (
    import_batch, import_record)
from openerp.addons.connector_redmine.tests import test_connector_redmine

from ..unit import mapper
from ..unit import backend_adapter
from ..unit import import_synchronizer

from mock import patch
from datetime import datetime

reload(test_connector_redmine)
reload(mapper)
reload(backend_adapter)
reload(import_synchronizer)


import_job_path = (
    'openerp.addons.connector_redmine.unit.import_synchronizer.'
    'import_record.delay')


def mock_delay(session, model_name, *args, **kwargs):
    """Enqueue the function. Return the uuid of the created job."""
    return import_record(session, model_name, *args, **kwargs)


class test_import_time_entries(common.TransactionCase):

    def setUp(self):
        super(test_import_time_entries, self).setUp()
        self.backend_model = self.env['redmine.backend']
        self.user_model = self.env["res.users"]
        self.employee_model = self.env['hr.employee']
        self.timesheet_model = self.env['hr_timesheet_sheet.sheet']
        self.account_model = self.env['account.analytic.account']
        self.redmine_model = self.env['redmine.hr.analytic.timesheet']
        self.general_account_model = self.env['account.account']
        self.product_model = self.env['product.product']

        self.user_1 = self.user_model.create({
            'name': 'User 1',
            'login': 'user_1',
        })

        journal = self.env.ref('hr_timesheet.analytic_journal')

        self.account = self.account_model.create({
            'type': 'contract',
            'name': 'Test Redmine',
            'code': 'abcd',
            'to_invoice': self.ref(
                'hr_timesheet_invoice.timesheet_invoice_factor2'),
        })

        self.account_2 = self.account_model.create({
            'type': 'contract',
            'name': 'Test Redmine',
            'code': 'efgh',
            'to_invoice': self.ref(
                'hr_timesheet_invoice.timesheet_invoice_factor1'),
        })

        self.product = self.product_model.search(
            [('type', '=', 'service')])[0]

        self.general_account = self.general_account_model.create({
            'type': 'other',
            'code': '123123',
            'name': 'test',
            'user_type': self.ref('account.data_account_type_expense'),
        })

        self.product.write({
            'property_account_expense': self.general_account.id,
            'standard_price': 30,
        })

        self.employee = self.employee_model.create({
            'name': 'Employee 1',
            'user_id': self.user_1.id,
            'journal_id': journal.id,
            'product_id': self.product.id,
        })

        self.backend = self.backend_model.create({
            'name': 'redmine_test',
            'location': 'http://localhost:3000',
            'key': '39730056c1df6fb97b4fa5b9eb4bd37221ca1223',
            'version': '1.3',
            'contract_ref': 'contract_ref_field',
            'is_default': True,
        })

        env = self.env
        cr, uid, context = env.cr, env.uid, env.context
        self.session = RedmineConnectorSession(cr, uid, context=context)

        self.environment = ConnectorEnvironment(
            self.backend, self.session, 'redmine.hr.analytic.timesheet')

    def get_time_entry_defaults(self):
        return {
            'spent_on': '2015-01-01',
            'hours': 8.5,
            'issue_id': 456,
            'issue_subject': 'Test Mapping of Time Entry',
            'contract_ref': 'abcd',
            'project_name': 'Test Time Entry',
            'updated_on': datetime(2015, 4, 8, 20, 38, 31),
            'user_login': 'user_1',
            'redmine_id': 123,
        }

    def test_01_mapper_analytic_account(self):
        """
        Test that the proper analytic account is mapped
        """
        mapper_obj = mapper.TimeEntryImportMapper(self.environment)

        defaults = self.get_time_entry_defaults()
        map_record = mapper_obj.map_record(defaults)
        res = map_record.values(for_create=True)

        self.assertEqual(res['account_id'], self.account.id)

        defaults['contract_ref'] = 'efgh'
        map_record = mapper_obj.map_record(defaults)
        res = map_record.values()

        self.assertEqual(res['account_id'], self.account_2.id)

    @patch(import_job_path, side_effect=mock_delay)
    def import_time_entry_batch(
        self, record_id, defaults, job_decorator, options=None
    ):
        adapter = backend_adapter.TimeEntryAdapter
        with patch.object(adapter, 'read') as read, \
                patch.object(adapter, 'search') as search:

            search.return_value = [record_id]
            read.return_value = defaults

            import_batch(
                self.session, 'redmine.hr.analytic.timesheet',
                self.backend.id, filters={
                    'from_date': '2015-01-01',
                    'to_date': '2015-01-07',
                }, options=options)

    def test_02_binder(self):
        binder = RedmineModelBinder(self.environment)
        mapper_obj = mapper.TimeEntryImportMapper(self.environment)

        defaults = self.get_time_entry_defaults()
        map_record = mapper_obj.map_record(defaults)
        data = map_record.values(for_create=True)

        binding_id = self.env['redmine.hr.analytic.timesheet'].create(data).id

        binder.bind(123, binding_id)

    def test_03_import_batch_synchronizer(self):
        defaults = self.get_time_entry_defaults()
        self.import_time_entry_batch(123, defaults)

        timesheet = self.redmine_model.search([('redmine_id', '=', 123)])[0]

        self.assertEqual(timesheet.account_id, self.account)
        self.assertEqual(timesheet.unit_amount, 8.5)
        self.assertEqual(timesheet.date, '2015-01-01')
        self.assertEqual(timesheet.user_id, self.user_1)
        self.assertEqual(timesheet.product_id.id, self.product.id)
        self.assertEqual(timesheet.amount, -8.5 * 30)

        defaults['contract_ref'] = 'efgh'
        defaults['hours'] = 10
        defaults['spent_on'] = '2015-01-02'
        self.import_time_entry_batch(123, defaults)

        self.backend.refresh()
        self.assertEqual(
            self.backend.time_entry_last_update,
            datetime(2015, 4, 8, 20, 38, 31).strftime(
                DEFAULT_SERVER_DATETIME_FORMAT))

        timesheet.refresh()
        self.assertEqual(timesheet.account_id, self.account_2)
        self.assertEqual(timesheet.unit_amount, 10)
        self.assertEqual(timesheet.date, '2015-01-02')

    def test_04_cron_job(self):
        """
        Test that the import cron job executes without error
        """
        self.backend_model.prepare_time_entry_import()

    def test_05_import_single_user_time_entries_mapping_error(self):
        adapter = backend_adapter.TimeEntryAdapter
        with patch.object(adapter, 'search_user') as search_user, \
                patch.object(adapter, 'read') as read, \
                patch.object(adapter, 'search') as search:

            defaults = self.get_time_entry_defaults()

            updated_on = self.backend.time_entry_last_update

            search_user.return_value = 1
            search.return_value = [1, 2]

            def side_effect(redmine_id):
                if redmine_id == 1:
                    return defaults
                return dict(defaults, contract_ref='not mapped')

            read.side_effect = side_effect

            timesheet = self.timesheet_model.create({
                'user_id': self.user_1.id,
                'employee_id': self.employee.id,
                'date_from': '2015-01-01',
                'date_to': '2015-01-07',
            })

            timesheet.import_timesheets_from_redmine()

            # Time entry 1 is mapped, but entry 2 is not mapped.
            # So one is created and the other is logged in the chatter.
            self.assertEqual(len(timesheet.timesheet_ids), 1)

            entry = timesheet.timesheet_ids[0]
            self.assertEqual(entry.to_invoice.id, self.ref(
                'hr_timesheet_invoice.timesheet_invoice_factor2'))

            self.backend.refresh()

            # Backend field time_entry_last_update must not be updated when
            # querying timesheets for a single user
            self.assertEqual(updated_on, self.backend.time_entry_last_update)
