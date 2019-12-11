# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import ValidationError

from odoo.tools.translate import _


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

        backend = self.env['redmine.backend'].sudo().search([
            ('is_default', '=', True),
        ], limit=1)

        if not backend:
            raise ValidationError(
                _('Their is no Redmine backend configured '
                    'to import time entries.'))

        employee = self.employee_id

        if not employee.user_id:
            raise ValidationError(
                _('The employee %s is not related to a user.') %
                employee.name)

        user = employee.user_id
        if user.redmine_backend_id:
            if not user.redmine_backend_id:
                raise ValidationError(
                    _('The redmine service %s is inactive. '
                      'Please change it in your user preferences or '
                      'contact your system administrator.') %
                    employee.name)
            backend = user.redmine_backend_id

        filters = {
            'login': employee.user_id.login,
            'from_date': self.date_from,
            'to_date': self.date_to,
        }
        with backend.work_on('redmine.account.analytic.line') as work:
            importer = work.component(usage='batch.importer')
            mapping_errors = importer.run_single_user(filters=filters)

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
