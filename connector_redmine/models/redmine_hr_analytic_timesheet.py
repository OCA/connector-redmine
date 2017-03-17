# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class RedmineTimeEntry(models.Model):
    _name = 'redmine.account.analytic.line'
    _description = 'Redmine Time Entry Binding'
    _inherit = 'redmine.binding'
    _inherits = {'account.analytic.line': 'openerp_id'}

    openerp_id = fields.Many2one(
        'account.analytic.line', 'Timesheet', required=True,
        ondelete='cascade'
    )
