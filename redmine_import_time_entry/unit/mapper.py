# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tools.translate import _
from openerp.addons.connector_redmine.backend import redmine
from openerp.addons.connector_redmine.unit.mapper import RedmineImportMapper
from openerp.addons.connector.unit.mapper import mapping
from openerp.addons.connector.exception import MappingError


@redmine
class TimeEntryImportMapper(RedmineImportMapper):
    _model_name = 'redmine.hr.analytic.timesheet'

    direct = [
        ('spent_on', 'date'),
        ('hours', 'unit_amount'),
        ('entry_id', 'redmine_id'),
    ]

    @mapping
    def name(self, record):
        name = self.backend_record.location

        issue_id = record['issue_id']

        if issue_id:
            if name[-1] != '/':
                name += '/'

            name += ('issues/%d - %s') % (
                issue_id, record['issue_subject'])

        return {'name': name}

    @mapping
    def account_id(self, record):
        account_obj = self.env['account.analytic.account']

        accounts = account_obj.search([
            ('type', '=', 'contract'),
            ('code', '=', record['contract_ref']),
        ])

        if not accounts:
            raise MappingError(
                _('No analytic account found for the Redmine project '
                    '%(contract_ref)s - %(project_name)s.') % {
                    'contract_ref': record['contract_ref'],
                    'project_name': record['project_name'],
                })

        account = accounts[0]

        return {
            'account_id': account.id,
            'to_invoice': account.to_invoice.id,
        }

    @mapping
    def user_id(self, record):
        user = self.env['res.users'].search([
            ('login', '=', record['user_login']),
        ])

        if not user:
            raise MappingError(
                _('No user found with login %s.') % (record['user_login']))

        return {'user_id': user.id}

    @mapping
    def journal_id(self, record):
        user_id = self.user_id(record)['user_id']
        user = self.env['res.users'].browse(user_id)

        if not user.employee_ids:
            raise MappingError(
                _('User %s has no related employee.') % user.name)

        employee = user.employee_ids[0]

        if not employee.journal_id:
            raise MappingError(
                _('Employee %s has no analytic journal.') % employee.name)

        return {'journal_id': employee.journal_id.id}

    @mapping
    def general_account_id(self, record):
        user_id = self.user_id(record)['user_id']

        timesheet_model = self.env['hr.analytic.timesheet']
        account_id = timesheet_model.with_context(
            user_id=user_id)._getGeneralAccount()

        return {
            'general_account_id': account_id,
        }

    @mapping
    def product_id(self, record):
        user_id = self.user_id(record)['user_id']

        timesheet_model = self.env['hr.analytic.timesheet']

        product_uom_id = timesheet_model.with_context(
            user_id=user_id)._getEmployeeUnit()
        product_id = timesheet_model.with_context(
            user_id=user_id)._getEmployeeProduct()

        product = self.env['product.product'].browse(product_id)

        return {
            'product_id': product_id,
            'product_uom_id': product_uom_id,
            'amount': -record['hours'] * product.standard_price,
        }
