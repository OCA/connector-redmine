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

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.addons.connector_redmine.unit.import_synchronizer import (
    import_batch)
from openerp.addons.connector.session import ConnectorSession
from openerp.tools import (
    DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT)

from datetime import datetime, timedelta

from tools import ustr

import logging
_logger = logging.getLogger(__name__)


class redmine_backend(orm.Model):
    _inherit = 'redmine.backend'

    _columns = {
        'contract_ref': fields.char(
            'Contract # field name',
            help="The field in Redmine used to relate a project in Redmine "
            "to a project in Odoo. Each redmine project must have a unique "
            "value for this attribute."
        ),
        'time_entry_last_update': fields.datetime(
            'Last Time Entry Update', required=True,
        ),
        'time_entry_import_activate': fields.boolean(
            'Activate Time Entry Import'
        ),
        'time_entry_number_of_days': fields.integer(
            'Time Entries - Number of days',
            help="Number of days used when fetching the time entries.",
            required=True
        )
    }

    _defaults = {
        'time_entry_import_activate': True,
        'time_entry_number_of_days': 14,

        # At the first import, this field must have a value so that the
        # update_on field on Redmine time entries can be compared to it
        # Comparing False with a datetime object raises an error.
        'time_entry_last_update': datetime(1900, 1, 1).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT),
    }

    def _check_time_entry_import_activate(
        self, cr, uid, ids, context=None
    ):
        backend_ids = self.search(cr, uid, [
            ('time_entry_import_activate', '=', True)], context=context)

        if len(backend_ids) > 1:
            return False

        return True

    _constraints = [
        (
            _check_time_entry_import_activate,
            "You can not have more that one Redmine backend with "
            "time entry import activated."
            ['time_entry_import_activate'],
        ),
    ]

    def check_contract_ref(self, cr, uid, ids, context=None):
        """
        Check if the contract_ref field exists in redmine
        """
        assert len(ids) == 1, "Only 1 id expected"
        backend = self.browse(cr, uid, ids[0], context=context)
        adapter = self._get_base_adapter(cr, uid, ids, context=context)

        try:
            adapter._auth()
        except Exception as e:
            raise orm.except_orm(
                type(e), _('Could not connect to Redmine: %s') % ustr(e))

        projects = adapter.redmine_api.project.all()
        exist = False

        if projects:
            for cs in projects[0].custom_fields:
                if cs['name'] == backend.contract_ref:
                    exist = True

        if exist is True:
            raise orm.except_orm(_('Connection test succeeded!'),
                                 _('Everything seems properly set up!'))
        else:
            raise orm.except_orm(
                _('Redmine backend configuration error!'),
                _("The contract # field name doesn't exist.")
            )

    def prepare_time_entry_import(self, cr, uid, context=None):

        backend_ids = self.search(cr, uid, [
            ('time_entry_import_activate', '=', True)], context=context)

        for backend in self.browse(cr, uid, backend_ids, context=context):

            today = datetime.now()
            date_to = today.strftime(DEFAULT_SERVER_DATE_FORMAT)
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
