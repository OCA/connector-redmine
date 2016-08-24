# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tools.translate import _
from openerp.addons.connector.exception import (
    NetworkRetryableError, FailedJobError, InvalidDataError)
from openerp.addons.connector.unit.backend_adapter import BackendAdapter
from openerp.tools import ustr
from redmine import Redmine, exceptions
from requests.exceptions import ConnectionError


class RedmineAdapter(BackendAdapter):
    """
    Backend Adapter for Redmine

    Read methods must return a python dictionary and search methods a list
    of ids.

    If a Redmine record is not found in a read method, the return value
    must be None.

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
        self._auth()

        users = self.redmine_api.user.filter(name=login)

        user_id = next(
            (user.id for user in users if user.login == login), False)

        if not user_id:
            raise InvalidDataError(
                _("No user with login %s found in Redmine.") % login)

        return user_id
