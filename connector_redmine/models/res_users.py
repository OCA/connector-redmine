# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ResUsers(models.Model):

    _inherit = 'res.users'

    redmine_backend_ids = fields.Many2many(
        'redmine.backend', string='Redmine Server',
        help="The redmine service from which to import "
        "your timesheets. If empty, the default redmine service "
        "will be used instead.")

    def __init__(self, pool, cr):
        super(ResUsers, self).__init__(pool, cr)
        self.SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        self.SELF_WRITEABLE_FIELDS.extend(['redmine_backend_ids'])
