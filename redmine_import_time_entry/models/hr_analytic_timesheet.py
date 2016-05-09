# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class HrAnalyticTimesheet(models.Model):
    _inherit = 'hr.analytic.timesheet'

    @api.model
    def create(self, vals):
        """
        The base create method checks in context for the user_id.

        By default, the mapper passes the fields through vals,
        so need to update the context.
        """
        context = self.env.context

        if not context.get('user_id', False):
            self = self.with_context(user_id=False)

        return super(HrAnalyticTimesheet, self).create(vals)
