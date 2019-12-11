# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.tools import ustr
from odoo.exceptions import UserError

from datetime import datetime, timedelta


import logging
_logger = logging.getLogger(__name__)


to_string = fields.Date.to_string


class redmine_backend(models.Model):
    _inherit = 'redmine.backend'

    contract_ref = fields.Char(
        'Contract # field name',
        help="The field in Redmine used to relate a project in Redmine "
        "to a project in Odoo. Each redmine project must have a unique "
        "value for this attribute."
    )
    sync_tasks = fields.Boolean(
        "Sync Versions -> Tasks",
        help="Redmine Versions will be synchronized with Odoo tasks, "
             "using their name to match")
    time_entry_last_update = fields.Datetime(
        'Last Time Entry Update', required=True,
        # At the first import, this field must have a value so that the
        # update_on field on Redmine time entries can be compared to it
        # Comparing False with a datetime object raises an error.
        default=lambda self: datetime(1900, 1, 1)
    )
    time_entry_number_of_days = fields.Integer(
        'Time Entries - Number of days',
        help="Number of days used when fetching the time entries.",
        required=True,
        default=14,
    )

    @api.multi
    def check_contract_ref(self):
        """
        Check if the contract_ref field exists in redmine
        """
        self.ensure_one()
        with self.work_on('redmine.backend') as work:
            adapter = work.component(usage='backend.adapter')

        try:
            adapter._auth()
        except Exception as e:
            raise UserError(
                'Could not connect to Redmine: %s' % ustr(e))

        projects = adapter.redmine_api.project.all()
        exist = False

        if projects:
            if hasattr(projects[0], 'custom_fields'):
                for cs in projects[0].custom_fields:
                    if cs['name'] == self.contract_ref:
                        exist = True
            elif hasattr(projects[0], self.contract_ref):
                exist = True

        if exist is True:
            raise UserError(
                _('Connection test succeeded\n'
                  'Everything seems properly set up'))
        else:
            raise UserError(
                _("Redmine backend configuration error\n"
                  "The contract # field name doesn't exist.")
            )

    @api.model
    def prepare_time_entry_import(self):
        backends = self.search([])
        for backend in backends:
            today = datetime.now()
            date_to = to_string(today)
            date_from = to_string(today - timedelta(
                days=backend.time_entry_number_of_days))
            filters = {
                'from_date': date_from,
                'to_date': date_to,
            }
            model = 'redmine.account.analytic.line'
            _logger.info(
                'Scheduling time entry batch synchronization from Redmine '
                'with backend %s.' % backend.name)
            self.env[model].with_delay().import_batch(backend, filters=filters)
            self.env[model].with_delay().delete_batch(backend, filters=filters)
