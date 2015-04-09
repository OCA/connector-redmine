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

from openerp.tools.translate import _
from openerp.addons.connector.exception import (
    NetworkRetryableError, FailedJobError, InvalidDataError)
from openerp.addons.connector.unit.backend_adapter import CRUDAdapter
from redmine import Redmine, exceptions
from requests.exceptions import ConnectionError

from tools import ustr


class RedmineAdapter(CRUDAdapter):
    """
    Backend Adapter for Redmine

    Read methods must return a python dictionary and search methods a list
    of ids.

    This is important because it allows to mock the adapter easily
    in unit tests.
    """
    def _auth(self):
        auth_data = self.backend_record.read(['location', 'key'])[0]

        try:
            redmine_api = Redmine(
                auth_data['location'],
                key=auth_data['key'],
            )
            redmine_api.auth()

        except (exceptions.AuthError, ConnectionError) as err:
            raise FailedJobError(
                _('Redmine connection Error: '
                    'Invalid authentications key.'))

        except (exceptions.UnknownError, exceptions.ServerError) as err:
            raise NetworkRetryableError(
                _('A network error caused the failure of the job: '
                    '%s') % ustr(err))

        self.redmine_api = redmine_api

    def search_user(self, login):
        """
        Get a Redmine user id from a Odoo login
        """
        users = self.redmine_api.user.filter(name=login)

        user_id = next(
            (user.id for user in users if user.login == login), False)

        if not user_id:
            raise InvalidDataError(
                _("No user with login %s found in Redmine.") % login)

        return user_id
