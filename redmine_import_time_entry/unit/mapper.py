# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tools.translate import _
from odoo.addons.connector.unit.mapper import mapping
from odoo.addons.connector.exception import MappingError
from odoo.addons.component.core import Component


class TimeEntryImportMapper(Component):
    _name = 'redmine.account.analytic.line.mapper'
    _inherit = 'redmine.import.mapper'
    _apply_on = 'redmine.account.analytic.line'

    direct = [
        ('spent_on', 'date'),
        ('hours', 'unit_amount'),
        ('entry_id', 'redmine_id'),
    ]

    @mapping
    def name(self, record):
        name = self.backend_record.location
        if record.get('comments'):
            name = "%s - %s" % (record['comments'], name)

        issue_id = record['issue_id']

        if issue_id:
            if name[-1] != '/':
                name += '/'

            name += ('issues/%d - %s') % (
                issue_id, record['issue_subject'])

        return {'name': name}

    @mapping
    def account_id(self, record):
        project_obj = self.env['project.project']

        projects = project_obj.search([
            ('code', '=', record['contract_ref']),
        ])

        if not projects:
            projects = project_obj.search([
                ('name', '=', record['contract_ref']),
            ])

        if not projects:
            raise MappingError(
                _('No project found for '
                    '%(contract_ref)s - %(project_name)s.') % {
                    'contract_ref': record['contract_ref'],
                    'project_name': record['project_name'],
                })
        if len(projects) > 1:
            raise MappingError(_(
                "Too many projects for "
                "%(contract_ref)s - %(project_name)s."
            ) % {
                    'contract_ref': record['contract_ref'],
                    'project_name': record['project_name'],
                })

        project = projects[0]
        res = {
            'project_id': project.id,
        }

        if record.get('version'):
            task = self.env['project.task'].search([
                ('project_id', '=', project.id),
                ('name', '=', record['version'])
            ])
            if len(task) == 1:
                res['task_id'] = task.id

        return res

    @mapping
    def user_id(self, record):
        user = None
        if record.get('user_login'):
            user = self.env['res.users'].search([
                ('login', '=', record['user_login']),
            ])
            if not user:
                raise MappingError(
                    _('No user found with login %s.') % (record['user_login']))
        elif record.get('user_name'):
            user = self.env['res.users'].search([
                ('name', '=', record['user_name']),
            ])
            if not user:
                raise MappingError(
                    _('No user found with name %s.') % (record['user_name']))
        if not user:
            raise MappingError(
                _('No user found for record %s.') % (record['entry_id']))

        return {'user_id': user.id}
