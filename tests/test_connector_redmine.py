# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 - Present Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests.common import TransactionCase
from openerp.tools import (DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT)
from openerp.addons.connector.connector import ConnectorEnvironment
from openerp.addons.connector.session import ConnectorSession
from ..unit.mapper import RedmineImportMapper
from ..unit.binder import RedmineModelBinder
from ..unit.import_synchronizer import RedmineImportSynchronizer
from datetime import datetime


class TestRedmineConnector(TransactionCase):
    def setUp(self):
        super(TestRedmineConnector, self).setUp()
        self.backend_model = self.env['redmine.backend']
        self.user_model = self.env['res.users']
        self.employee_model = self.env['hr.employee']
        self.timesheet_model = self.env['hr.analytic.timesheet']
        self.account_model = self.env['account.analytic.account']
        self.redmine_model = self.env['redmine.hr.analytic.timesheet']

        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context

        self.user_id = self.user_model.create(
            cr, uid, {
                'name': 'User 1',
                'login': 'user_1',
            }, context=context)

        self.user = self.user_model.browse(
            cr, uid, self.user_id, context=context)

        journal_id = self.env.ref('hr_timesheet.analytic_journal').id

        self.account_id = self.account_model.create(cr, uid, {
            'type': 'contract',
            'name': 'Test Redmine',
            'code': 'abcd',
        }, context=context)

        self.employee_id = self.employee_model.create(
            cr, uid, {
                'name': 'Employee 1',
                'user_id': self.user_id,
                'journal_id': journal_id,
            }, context=context)

        self.backend_id = self.backend_model.create(cr, uid, {
            'name': 'redmine_test',
            'location': 'http://localhost:3000',
            'key': '39730056c1df6fb97b4fa5b9eb4bd37221ca1223',
            'version': '1.3',
        }, context=context)

        self.backend = self.backend_model.browse(
            cr, uid, self.backend_id, context=context)

        self.session = ConnectorSession(cr, uid, context=context)
        self.environment = ConnectorEnvironment(
            self.backend, self.session, 'redmine.hr.analytic.timesheet')

        self.now = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.date_now = datetime.now().date().strftime(
            DEFAULT_SERVER_DATE_FORMAT)

        self.timesheet_vals = {
            'redmine_id': 123,
            'updated_on': self.now,
            'backend_id': self.backend.id,
            'sync_date': self.now,
            'user_id': self.user_id,
            'date': self.date_now,
            'account_id': self.account_id,
            'unit_amount': 5,
            'name': 'Test',
        }

        self.redmine_timesheet_id = self.redmine_model.create(
            cr, uid, self.timesheet_vals, context=context)

    def test_redmine_mapper(self):
        mapper = RedmineImportMapper(self.environment)

        update = datetime(2015, 1, 1, 8, 32, 10)
        record = {'updated_on': update}

        self.assertEqual(
            mapper.updated_on(record),
            {'updated_on': update.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

        self.assertEqual(
            mapper.backend_id(record), {'backend_id': self.backend.id})

        now = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.assertEqual(mapper.sync_date(record), {'sync_date': now})

    def test_redmine_binder_to_openerp(self):
        cr, uid, context = self.cr, self.uid, self.context
        binder = RedmineModelBinder(self.environment)

        # Without the unwrap parameter, to_openerp must return
        # the ID of the binding (redmine.hr.analytic.timesheet)
        timesheet_id = binder.to_openerp(123)
        timesheet = self.redmine_model.browse(
            cr, uid, timesheet_id, context=context)

        self.assertEqual(timesheet.date, self.date_now)
        self.assertEqual(timesheet.redmine_id, 123)

        # With the unwrap parameter, to_openerp must return
        # the ID of the openerp model record (hr.analytic.timesheet)
        timesheet_id = binder.to_openerp(123, unwrap=True)
        timesheet = self.timesheet_model.browse(
            cr, uid, timesheet_id, context=context)

        self.assertEqual(timesheet.date, self.date_now)

    def test_redmine_binder_to_backend(self):
        cr, uid, context = self.cr, self.uid, self.context
        binder = RedmineModelBinder(self.environment)

        timesheet = self.redmine_model.browse(
            cr, uid, self.redmine_timesheet_id, context=context)

        redmine_id = binder.to_backend(timesheet.openerp_id.id, wrap=True)
        redmine_id_2 = binder.to_backend(self.redmine_timesheet_id)

        self.assertEqual(redmine_id, redmine_id_2)
        self.assertEqual(redmine_id, 123)

    def test_redmine_binder_unwrap_binding(self):
        cr, uid, context = self.cr, self.uid, self.context
        binder = RedmineModelBinder(self.environment)

        timesheet_id = binder.unwrap_binding(self.redmine_timesheet_id)

        timesheet = self.timesheet_model.browse(
            cr, uid, timesheet_id, context=context)

        self.assertEqual(timesheet.date, self.date_now)

        timesheet_2 = binder.unwrap_binding(
            self.redmine_timesheet_id, browse=True)

        self.assertEqual(timesheet, timesheet_2)

    def test_redmine_binder_unwrap_model(self):
        binder = RedmineModelBinder(self.environment)

        self.assertEqual(binder.unwrap_model(), 'hr.analytic.timesheet')

    def test_import_synchronizer_get_binding_id(self):
        cr, uid, context = self.cr, self.uid, self.context
        synchronizer = RedmineImportSynchronizer(self.environment)

        binding_id = self.redmine_model.search(cr, uid, [
            ('redmine_id', '=', 123)
        ], context=context)[0]

        synchronizer.redmine_id = 123
        self.assertEqual(synchronizer._get_binding_id(), binding_id)

    def test_import_synchronizer_update(self):
        cr, uid, context = self.cr, self.uid, self.context
        synchronizer = RedmineImportSynchronizer(self.environment)

        synchronizer.redmine_id = 123

        new_vals = {
            'name': 'New Name',
            'unit_amount': 10,
        }
        synchronizer._update(synchronizer._get_binding_id(), new_vals)

        timesheet = self.redmine_model.browse(
            cr, uid, self.redmine_timesheet_id, context=context)

        for val in new_vals:
            self.assertEqual(new_vals[val], timesheet[val])

    def test_import_synchronizer_create(self):
        cr, uid, context = self.cr, self.uid, self.context
        synchronizer = RedmineImportSynchronizer(self.environment)
        synchronizer.redmine_id = 345

        vals = self.timesheet_vals
        vals['redmine_id'] = 345
        vals['name'] = 'Second Timesheet'

        binding_id = synchronizer._create(vals)

        binding = self.redmine_model.browse(
            cr, uid, binding_id, context=context)

        self.assertEqual(binding.name, vals['name'])
