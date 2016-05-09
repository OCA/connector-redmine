# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2016 - Present Savoir-faire Linux
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

from openerp import api, fields, models
from openerp.exceptions import ValidationError
from openerp.tools.translate import _
from openerp.addons.connector_redmine.unit.import_synchronizer import (
    import_batch)
from openerp.addons.connector.session import ConnectorSession
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
    time_entry_import_activate = fields.Boolean(
        'Activate Time Entry Import',
        default=True,
    )
    time_entry_number_of_days = fields.Integer(
        'Time Entries - Number of days',
        help="Number of days used when fetching the time entries.",
        required=True,
        default=14,
    )

    @api.constrains('time_entry_import_activate')
    def _check_time_entry_import_activate(self):
        backend_ids = self.search([
            ('time_entry_import_activate', '=', True)])

        if len(backend_ids) > 1:
            raise ValidationError(_(
                "You can not have more that one Redmine backend with "
                "time entry import activated."
            ))

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
        backends = self.search([
            ('time_entry_import_activate', '=', True)])

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

            session = ConnectorSession(cr, uid, context=context)
            model = 'redmine.hr.analytic.timesheet'

            _logger.info(
                'Scheduling time entry batch import from Redmine '
                'with backend %s.' % backend.name)
            import_batch.delay(session, model, backend.id, filters=filters)
