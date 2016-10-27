# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, SUPERUSER_ID
from openerp.exceptions import ValidationError

from openerp.tools.translate import _
from openerp.addons.connector_redmine.session import RedmineConnectorSession
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

        session = RedmineConnectorSession(
            self.env.cr, SUPERUSER_ID, self.env.context)
        backends = self.env['redmine.backend'].sudo().search([
            ('is_default', '=', True),
        ])

        if not backends:
            raise ValidationError(
                _('Their is no Redmine backend configured '
                    'to import time entries.'))

        employee = self.employee_id

        if not employee.user_id:
            raise ValidationError(
                _('The employee %s is not related to a user.') %
                employee.name)

        user = employee.user_id
        if user.redmine_backend_ids:
            backends = user.redmine_backend_ids

        mapping_errors = []
        for backend in backends:
            mapping_errors += import_single_user_time_entries(
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
