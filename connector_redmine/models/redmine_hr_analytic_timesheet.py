# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class RedmineTimeEntry(models.Model):
    _name = 'redmine.hr.analytic.timesheet'
    _description = 'Redmine Time Entry Binding'
    _inherit = 'redmine.binding'
    _inherits = {'hr.analytic.timesheet': 'openerp_id'}

    openerp_id = fields.Many2one(
        'hr.analytic.timesheet', 'Timesheet', required=True,
        ondelete='cascade'
    )
