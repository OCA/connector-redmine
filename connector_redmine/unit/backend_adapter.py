# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tools.translate import _
import odoo.addons.connector.exception as cn_exception
from odoo.tools import ustr
from requests.exceptions import ConnectionError
from odoo.addons.component.core import AbstractComponent, Component

import logging
_logger = logging.getLogger(__name__)

try:
    from redminelib import Redmine, exceptions
except (ImportError, IOError) as err:
    _logger.warning('python-redmine not installed!')


class RedmineAdapter(AbstractComponent):
    """
    Backend Adapter for Redmine

    Read methods must return a python dictionary and search methods a list
    of ids.

    If a Redmine record is not found in a read method, the return value
    must be None.

    This is important because it allows to mock the adapter easily
    in unit tests.
    """

    _name = 'redmine.adapter'
    _inherit = ['base.backend.adapter', 'base.connector']
    _usage = 'backend.adapter'

    def _auth(self):
        auth_data = self.backend_record.read(['location', 'key'])[0]

        try:
            redmine_api = Redmine(
                auth_data['location'],
                key=auth_data['key'],
            )
            redmine_api.auth()

        except (exceptions.AuthError, ConnectionError) as e:
            raise cn_exception.FailedJobError(
                _('Redmine connection Error: '
                    'Invalid authentications key. (%s)') % e)

        except (exceptions.UnknownError, exceptions.ServerError) as e:
            raise cn_exception.NetworkRetryableError(
                _('A network error caused the failure of the job: '
                    '%s') % ustr(e))

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
            raise cn_exception.InvalidDataError(
                _("No user with login %s found in Redmine.") % login)

        return user_id

class BackendAdapter(Component):

    _name = 'redmine.backend.adapter'
    _inherit = 'redmine.adapter'
    _apply_on = 'redmine.backend'
