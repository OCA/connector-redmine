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

from openerp import api, models, SUPERUSER_ID
from openerp.exceptions import ValidationError

from openerp.tools.translate import _
from openerp.addons.connector.session import ConnectorSession
from ..unit.import_synchronizer import import_single_user_time_entries


class HrTimesheetSheet(models.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    @api.multi
    def import_timesheets_from_redmine(self):
        """
        Call the connector to import timesheets as superuser
        to prevent errors related with security issues.
        We ensure that the user has write access to the
        timesheet.
        """
        self.ensure_one()

        self.check_access_rule('write')

        session = ConnectorSession(self.env.cr, SUPERUSER_ID, self.env.context)
        backend = self.env['redmine.backend'].sudo().search(
            [('time_entry_import_activate', '=', True)], limit=1)

        if not backend:
            raise ValidationError(
                _('Their is no Redmine backend configured '
                    'to import time entries.'))

        employee = self.employee_id

        if not employee.user_id:
            raise ValidationError(
                _('The employee %s is not related to a user') %
                employee.name)

        mapping_errors = import_single_user_time_entries(
            session, backend.id, employee.user_id.login,
            self.date_from, self.date_to)

        if mapping_errors:
            part_1 = _(
                "Some time entries were not imported from Redmine.")
            part_2 = "\n".join({e.message for e in mapping_errors})
            body = "%s\n%s" % (part_1, part_2)

            # Log the message using SUPERUSER_ID, because otherwise
            # the user will not be notified by email and might
            # see that some entries were not imported.
            self.sudo().message_post(
                body=body, type='comment', subtype='mail.mt_comment',
                content_subtype='plaintext')
