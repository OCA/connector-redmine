# -*- coding: utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests import common
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

from openerp.addons.connector.connector import Environment
from openerp.addons.connector.session import ConnectorSession

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
        self.backend_model = self.registry('redmine.backend')
        self.user_model = self.registry("res.users")
        self.employee_model = self.registry('hr.employee')
        self.timesheet_model = self.registry('hr_timesheet_sheet.sheet')
        self.account_model = self.registry('account.analytic.account')
        self.redmine_model = self.registry('redmine.hr.analytic.timesheet')
        self.general_account_model = self.registry('account.account')
        self.product_model = self.registry('product.product')

        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context

        self.user_id = self.user_model.create(
            cr, uid, {
                'name': 'User 1',
                'login': 'user_1',
            }, context=context)

        self.user = self.user_model.browse(
            cr, uid, self.user_id, context=context)

        journal_id = self.registry('ir.model.data').get_object_reference(
            cr, uid, 'hr_timesheet', 'analytic_journal')[1]

        self.account_id = self.account_model.create(cr, uid, {
            'type': 'contract',
            'name': 'Test Redmine',
            'code': 'abcd',
        }, context=context)

        self.account_2_id = self.account_model.create(cr, uid, {
            'type': 'contract',
            'name': 'Test Redmine',
            'code': 'efgh',
        }, context=context)

        self.account_1 = self.account_model.browse(
            cr, uid, self.account_id, context=context)
        self.account_2 = self.account_model.browse(
            cr, uid, self.account_2_id, context=context)

        self.product_id = self.product_model.search(
            cr, uid, [('type', '=', 'service')], context=context)[0]

        self.general_account_id = self.general_account_model.create(
            cr, uid, {
                'type': 'other',
                'code': '123123',
                'name': 'test',
                'user_type': self.ref('account.data_account_type_expense'),
            }, context=context)

        self.product_model.write(cr, uid, [self.product_id], {
            'property_account_expense': self.general_account_id,
        }, context=context)

        self.employee_id = self.employee_model.create(
            cr, uid, {
                'name': 'Employee 1',
                'user_id': self.user_id,
                'journal_id': journal_id,
                'product_id': self.product_id,
            }, context=context)

        self.backend_id = self.backend_model.create(cr, uid, {
            'name': 'redmine_test',
            'location': 'http://localhost:3000',
            'key': '39730056c1df6fb97b4fa5b9eb4bd37221ca1223',
            'version': '1.3',
            'contract_ref': 'contract_ref_field',
        }, context=context)

        self.backend = self.backend_model.browse(
            cr, uid, self.backend_id, context=context)

        self.session = ConnectorSession(cr, uid, context=context)
        self.environment = Environment(
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

    def atest_mapper_analytic_account(self):
        """
        Test that the proper analytic account is mapped
        """
        mapper_obj = mapper.TimeEntryImportMapper(self.environment)

        defaults = self.get_time_entry_defaults()
        map_record = mapper_obj.map_record(defaults)
        res = map_record.values(for_create=True)

        self.assertEqual(res['account_id'], self.account_id)

        defaults['contract_ref'] = 'efgh'
        map_record = mapper_obj.map_record(defaults)
        res = map_record.values()

        self.assertEqual(res['account_id'], self.account_2_id)

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
                self.backend_id, filters={
                    'from_date': '2015-01-01',
                    'to_date': '2015-01-07',
                }, options=options)

    def test_binder(self):
        binder = RedmineModelBinder(self.environment)
        mapper_obj = mapper.TimeEntryImportMapper(self.environment)

        defaults = self.get_time_entry_defaults()
        map_record = mapper_obj.map_record(defaults)
        data = map_record.values(for_create=True)

        binding_id = self.session.create('redmine.hr.analytic.timesheet', data)

        binder.bind(123, binding_id)

    def test_import_batch_synchronizer(self):
        cr, uid, context = self.cr, self.uid, self.context

        defaults = self.get_time_entry_defaults()
        self.import_time_entry_batch(123, defaults)

        ts_id = self.redmine_model.search(
            cr, uid, [('redmine_id', '=', 123)], context=context)[0]

        timesheet = self.redmine_model.browse(
            cr, uid, ts_id, context=context)

        self.assertEqual(timesheet.account_id, self.account_1)
        self.assertEqual(timesheet.unit_amount, 8.5)
        self.assertEqual(timesheet.date, '2015-01-01')
        self.assertEqual(timesheet.user_id, self.user)

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

    def test_cron_job(self):
        """
        Test that the import cron job executes without error
        """
        cr, uid, context = self.cr, self.uid, self.context
        self.backend_model.prepare_time_entry_import(cr, uid, context=context)

    def test_import_single_user_time_entries(self):
        adapter = backend_adapter.TimeEntryAdapter
        with patch.object(adapter, 'search_user') as search_user, \
                patch.object(adapter, 'read') as read, \
                patch.object(adapter, 'search') as search:

            defaults = self.get_time_entry_defaults()

            updated_on = self.backend.time_entry_last_update

            search_user.return_value = 1
            search.return_value = [1]
            read.return_value = defaults

            import_synchronizer.import_single_user_time_entries(
                self.session, self.backend_id,
                self.user.login, '2015-01-01', '2015-01-07')

            self.backend.refresh()

            # Backend field time_entry_last_update must not be updated when
            # querying timesheets for a single user
            self.assertEqual(updated_on, self.backend.time_entry_last_update)
