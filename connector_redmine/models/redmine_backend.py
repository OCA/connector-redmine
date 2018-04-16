# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import Warning
from odoo.tools.translate import _


class RedmineBackend(models.Model):
    _name = 'redmine.backend'
    _description = 'Redmine Backend'
    _inherit = 'connector.backend'
    _rec_name = 'location'

    def _select_versions(self):
        return [('1.3', _('1.3 and higher'))]

    location = fields.Char(
        'Location',
        size=128,
        required=True,
    )
    key = fields.Char(
        'Key',
        size=64,
        required=True,
        groups="connector.group_connector_manager",
    )
    version = fields.Selection(
        _select_versions,
        string='Version',
        required=True
    )

    is_default = fields.Boolean('Default Redmine Service')

    @api.multi
    def check_auth(self):
        """
        Check the authentication with Redmine
        """
        self.ensure_one()
        with self.work_on('redmine.backend') as work:
            adapter = work.component(usage='backend.adapter')

        try:
            adapter._auth()
        except Exception:
            raise Warning(_('Could not connect to Redmine'))

        raise Warning(
            _('Connection test succeeded'
              'Everything seems properly set up'))
