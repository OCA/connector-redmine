# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from openerp.tests.common import TransactionCase
from openerp.tools import (
    DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT)

from openerp.addons.connector.connector import ConnectorEnvironment
from openerp.addons.connector.backend import BACKENDS

from ..unit import mapper
from ..unit import binder
from ..unit import import_synchronizer
from ..unit import backend_adapter
from ..session import RedmineConnectorSession

from .. import backend, connector

# Clean the connector environment
# The module connector breaks the python environment when testing
# we need to reload the python modules so that the classes are
# registered again properly
BACKENDS.backends.clear()
reload(backend)
reload(connector)
reload(mapper)
reload(binder)
reload(import_synchronizer)
reload(backend_adapter)


class TestRedmineConnector(TransactionCase):

    def setUp(self):
        super(TestRedmineConnector, self).setUp()
        self.backend_model = self.env['redmine.backend']
        self.user_model = self.env['res.users']
        self.employee_model = self.env['hr.employee']
        self.timesheet_model = self.env['hr.analytic.timesheet']
        self.account_model = self.env['account.analytic.account']
        self.general_account_model = self.env['account.account']
        self.product_model = self.env['product.product']
        self.redmine_model = self.env['redmine.hr.analytic.timesheet']

        self.user_1 = self.user_model.create(
            {
                'name': 'User 1',
                'login': 'user_1',
            })

        journal = self.env.ref('hr_timesheet.analytic_journal')

        self.account = self.account_model.create({
            'type': 'contract',
            'name': 'Test Redmine',
            'code': 'abcd',
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
        })

        env = self.env
        cr, uid, context = env.cr, env.uid, env.context
        self.session = RedmineConnectorSession(cr, uid, context=context)
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
            'user_id': self.user_1.id,
            'date': self.date_now,
            'account_id': self.account.id,
            'unit_amount': 5,
            'name': 'Test',
        }

        self.redmine_timesheet = self.redmine_model.create(
            self.timesheet_vals)

    def test_01_redmine_mapper(self):
        mapper_obj = mapper.RedmineImportMapper(self.environment)

        update = datetime(2015, 1, 1, 8, 32, 10)
        record = {'updated_on': update}

        self.assertEqual(
            mapper_obj.updated_on(record),
            {'updated_on': update.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

        self.assertEqual(
            mapper_obj.backend_id(record), {'backend_id': self.backend.id})

        now = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.assertEqual(mapper_obj.sync_date(record), {'sync_date': now})

    def test_02_redmine_binder_to_openerp(self):
        binder_obj = binder.RedmineModelBinder(self.environment)

        # Without the unwrap parameter, to_openerp must return
        # the ID of the binding (redmine.hr.analytic.timesheet)
        timesheet_id = binder_obj.to_openerp(123)
        timesheet = self.redmine_model.browse(
            timesheet_id)

        self.assertEqual(timesheet.date, self.date_now)
        self.assertEqual(timesheet.redmine_id, 123)

        # With the unwrap parameter, to_openerp must return
        # the ID of the openerp model record (hr.analytic.timesheet)
        timesheet_id = binder_obj.to_openerp(123, unwrap=True)
        timesheet = self.timesheet_model.browse(
            timesheet_id)

        self.assertEqual(timesheet.date, self.date_now)

    def test_03_redmine_binder_to_backend(self):
        binder_obj = binder.RedmineModelBinder(self.environment)

        redmine_id = binder_obj.to_backend(
            self.redmine_timesheet.openerp_id.id, wrap=True)
        redmine_id_2 = binder_obj.to_backend(self.redmine_timesheet.id)

        self.assertEqual(redmine_id, redmine_id_2)
        self.assertEqual(redmine_id, 123)

    def test_04_redmine_binder_unwrap_binding(self):
        binder_obj = binder.RedmineModelBinder(self.environment)

        timesheet_id = binder_obj.unwrap_binding(self.redmine_timesheet.id)

        timesheet = self.timesheet_model.browse(
            timesheet_id)

        self.assertEqual(timesheet.date, self.date_now)

        timesheet_2 = binder_obj.unwrap_binding(
            self.redmine_timesheet.id, browse=True)

        self.assertEqual(timesheet, timesheet_2)

    def test_05_redmine_binder_unwrap_model(self):
        binder_obj = binder.RedmineModelBinder(self.environment)

        self.assertEqual(binder_obj.unwrap_model(), 'hr.analytic.timesheet')

    def test_06_import_synchronizer_get_binding_id(self):
        synchronizer = import_synchronizer.RedmineImportSynchronizer(
            self.environment)

        binding = self.redmine_model.search([('redmine_id', '=', 123)])[0]

        synchronizer.redmine_id = 123
        self.assertEqual(synchronizer._get_binding_id(), binding.id)

    def test_07_import_synchronizer_update(self):
        synchronizer = import_synchronizer.RedmineImportSynchronizer(
            self.environment)

        synchronizer.redmine_id = 123

        new_vals = {
            'name': 'New Name',
            'unit_amount': 10,
        }
        synchronizer._update(synchronizer._get_binding_id(), new_vals)

        for val in new_vals:
            self.assertEqual(new_vals[val], self.redmine_timesheet[val])

    def test_08_import_synchronizer_create(self):
        synchronizer = import_synchronizer.RedmineImportSynchronizer(
            self.environment)
        synchronizer.redmine_id = 345

        vals = self.timesheet_vals
        vals['redmine_id'] = 345
        vals['name'] = 'Second Timesheet'

        binding = synchronizer._create(vals)

        self.assertEqual(binding.name, vals['name'])
