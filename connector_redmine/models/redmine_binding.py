# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class RedmineBinding(models.AbstractModel):
    _name = 'redmine.binding'
    _inherit = 'external.binding'
    _description = 'Redmine Binding (Abstract)'

    backend_id = fields.Many2one(
        'redmine.backend', 'Redmine Backend', required=True,
        ondelete='restrict'
    )
    redmine_id = fields.Integer('ID in Redmine', required=True)
    sync_date = fields.Datetime(
        'Last Synchronization Date', required=True)
    updated_on = fields.Datetime('Last Update in Redmine')
