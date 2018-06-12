# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# © 2018 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import fields, models, api
from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)


class RedmineTimeEntry(models.Model):
    _name = 'redmine.account.analytic.line'
    _description = 'Redmine Time Entry Binding'
    _inherit = 'redmine.binding'
    _inherits = {'account.analytic.line': 'odoo_id'}

    odoo_id = fields.Many2one(
        'account.analytic.line', 'Timesheet', required=True,
        ondelete='cascade'
    )

    @job
    @api.model
    def delete_batch(self, backend, filters=None):
        with backend.work_on(self._name) as work:
            deleter = work.component(usage='batch.deleter')
            redmine_ids = deleter.get_all_records(filters=filters)
            deleted_lines = self.search([
                ('date', '>=', filters['from_date']),
                ('date', '<=', filters['to_date']),
                ('redmine_id', 'not in', redmine_ids)
            ])
            deleted_lines.mapped('odoo_id').unlink()
            if deleted_lines:
                _logger.debug(
                    'Deleted %s timesheet lines' % len(deleted_lines))

    @job
    @api.model
    def import_batch(self, backend, filters=None):
        with backend.work_on(self._name) as work:
            importer = work.component(usage='batch.importer')
            return importer.run(filters=filters)

    @job
    @api.model
    def import_record(self, backend, redmine_id):
        with backend.work_on(self._name) as work:
            importer = work.component(usage='record.importer')
            return importer.run(redmine_id)
