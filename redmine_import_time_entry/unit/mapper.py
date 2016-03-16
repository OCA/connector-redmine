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
        session = self.session

        account_ids = session.pool['account.analytic.account'].search(
            session.cr, session.uid, [
                ('type', '=', 'contract'),
                ('code', '=', record['contract_ref']),
            ], context=session.context)

        if not account_ids:
            raise MappingError(
                _('No analytic account found for the Redmine project '
                    '%(contract_ref)s - %(project_name)s.') % {
                    'contract_ref': record['contract_ref'],
                    'project_name': record['project_name'],
                })

        return {'account_id': account_ids[0]}

    @mapping
    def user_id(self, record):
        session = self.session
        cr, uid, context = session.cr, session.uid, session.context

        user_model = session.pool['res.users']

        user_ids = user_model.search(cr, uid, [
            ('login', '=', record['user_login']),
        ], context=context)

        if not user_ids:
            raise MappingError(
                _('No user found with login %s.') % (record['user_login']))

        user_id = user_ids[0]

        return {'user_id': user_id}

    @mapping
    def journal_id(self, record):
        session = self.session
        cr, uid, context = session.cr, session.uid, session.context

        user_id = self.user_id(record)['user_id']

        user_model = session.pool['res.users']
        user = user_model.browse(cr, uid, user_id, context=context)

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
        """
        Get the default expense account for the employee, using the
        default method of hr.analytic.timesheet.

        This ensures that the method is called with the proper
        context.
        """
        session = self.session
        cr, uid, context = session.cr, session.uid, session.context

        user_id = self.user_id(record)['user_id']

        timesheet_model = session.pool['hr.analytic.timesheet']
        ctx = dict(context, user_id=user_id)
        account_id = timesheet_model._getGeneralAccount(cr, uid, context=ctx)

        return {'general_account_id': account_id}
