# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.exceptions import Warning
from openerp.tools.translate import _
from openerp.addons.connector.connector import ConnectorEnvironment
from ..session import RedmineConnectorSession
from ..unit.backend_adapter import RedmineAdapter


class redmine_backend(models.Model):
    _name = 'redmine.backend'
    _description = 'Redmine Backend'
    _inherit = 'connector.backend'
    _backend_type = 'redmine'
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
    default_lang_id = fields.Many2one(
        'res.lang',
        'Default Language',
        help="If a default language is selected, the records "
             "will be imported in the translation of this language.\n"
             "Note that a similar configuration exists "
             "for each storeview.")

    is_default = fields.Boolean('Default Redmine Service')
    active = fields.Boolean('Active', default=True)

    @api.multi
    def get_base_adapter(self):
        """
        Get an adapter to test the backend connection
        """
        self.ensure_one()
        env = self.env
        cr, uid, context = env.cr, env.uid, env.context
        session = RedmineConnectorSession(cr, uid, context=context)
        environment = ConnectorEnvironment(self, session, None)

        return RedmineAdapter(environment)

    @api.multi
    def check_auth(self):
        """
        Check the authentication with Redmine
        """
        self.ensure_one()
        adapter = self.get_base_adapter()

        try:
            adapter._auth()
        except Exception:
            raise Warning(_('Could not connect to Redmine'))

        raise Warning(
            _('Connection test succeeded'
              'Everything seems properly set up'))
