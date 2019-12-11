# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class RedmineModelBinder(Component):
    _apply_on = [
        'redmine.account.analytic.line',
    ]
    _name = 'redmine.binder'
    _inherit = ['base.binder', 'base.connector']
    _external_field = 'redmine_id'
    _backend_field = 'backend_id'
    _odoo_field = 'odoo_id'
    _sync_date_field = 'sync_date'
