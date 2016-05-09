# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2016 - Present Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models
from openerp.exceptions import Warning
from openerp.tools.translate import _
from openerp.addons.connector.connector import ConnectorEnvironment
from openerp.addons.connector.session import ConnectorSession
from ..unit.backend_adapter import RedmineAdapter


class redmine_backend(models.Model):
    _name = 'redmine.backend'
    _description = 'Redmine Backend'
    _inherit = 'connector.backend'
    _backend_type = 'redmine'

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

    @api.multi
    def get_base_adapter(self):
        """
        Get an adapter to test the backend connection
        """
        self.ensure_one()
        env = self.env
        cr, uid, context = env.cr, env.uid, env.context
        session = ConnectorSession(cr, uid, context=context)
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
