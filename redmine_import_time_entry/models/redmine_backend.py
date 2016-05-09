# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.tools.translate import _
from openerp.addons.connector_redmine.unit.import_synchronizer import (
    import_batch)
from openerp.addons.connector_redmine.session import RedmineConnectorSession
from openerp.tools import ustr

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
        adapter = self.get_base_adapter()

        try:
            adapter._auth()
        except Exception as e:
            raise Warning(
                type(e), _('Could not connect to Redmine: %s') % ustr(e))

        projects = adapter.redmine_api.project.all()
        exist = False

        if projects:
            for cs in projects[0].custom_fields:
                if cs['name'] == self.contract_ref:
                    exist = True

        if exist is True:
            raise Warning(
                _('Connection test succeeded'
                  'Everything seems properly set up'))
        else:
            raise Warning(
                _("Redmine backend configuration error\n"
                  "The contract # field name doesn't exist.")
            )

    @api.model
    def prepare_time_entry_import(self):
        backends = self.search([])

        env = self.env
        cr, uid, context = env.cr, env.uid, env.context

        for backend in backends:

            today = datetime.now()
            date_to = to_string(today)
            date_from = today - timedelta(
                days=backend.time_entry_number_of_days)

            filters = {
                'from_date': date_from,
                'to_date': date_to,
            }

            session = RedmineConnectorSession(cr, uid, context=context)
            model = 'redmine.hr.analytic.timesheet'

            _logger.info(
                'Scheduling time entry batch import from Redmine '
                'with backend %s.' % backend.name)
            import_batch.delay(session, model, backend.id, filters=filters)
