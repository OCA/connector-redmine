# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 - Present Savoir-faire Linux
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

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.addons.connector.connector import Environment
from openerp.addons.connector.session import ConnectorSession
from ..unit.backend_adapter import RedmineAdapter


class redmine_backend(orm.Model):
    _name = 'redmine.backend'
    _description = 'Redmine Backend'
    _inherit = 'connector.backend'
    _backend_type = 'redmine'

    def _select_versions(self, cr, uid, context=None):
        return [('1.3', _('1.3 and higher'))]

    _columns = {
        'location': fields.char(
            'Location',
            size=128,
            required=True,
        ),
        'key': fields.char(
            'Key',
            size=64,
            required=True,
        ),
        'version': fields.selection(
            _select_versions,
            string='Version',
            required=True
        ),
        'default_lang_id': fields.many2one(
            'res.lang',
            'Default Language',
            help="If a default language is selected, the records "
                 "will be imported in the translation of this language.\n"
                 "Note that a similar configuration exists "
                 "for each storeview."),
    }

    def _get_base_adapter(self, cr, uid, ids, context=None):
        """
        Get an adapter to test the backend connection
        """
        backend = self.browse(cr, uid, ids[0], context=context)
        session = ConnectorSession(cr, uid, context=context)
        environment = Environment(backend, session, None)

        return RedmineAdapter(environment)

    def check_auth(self, cr, uid, ids, context=None):
        """ Check the authentication with Redmine """

        adapter = self._get_base_adapter(cr, uid, ids, context=context)

        try:
            adapter._auth()
        except Exception:
            raise orm.except_orm(
                _('Error'), _('Could not connect to Redmine'))

        raise orm.except_orm(_('Connection test succeeded'),
                             _('Everything seems properly set up'))
