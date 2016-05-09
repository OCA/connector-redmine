# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    _sql_constraints = [(
        'account_analytic_unique_reference',
        'unique(code)',
        'Reference must be unique'
    )]
