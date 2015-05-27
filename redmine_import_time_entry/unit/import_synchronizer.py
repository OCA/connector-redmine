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

from openerp.osv import orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _

from openerp.addons.connector.exception import ConnectorException

from openerp.addons.connector_redmine.backend import redmine
from openerp.addons.connector_redmine.connector import get_environment
from openerp.addons.connector_redmine.unit.import_synchronizer import (
    RedmineBatchImportSynchronizer, RedmineImportSynchronizer,
    import_record)

from datetime import datetime
from tools import ustr


@redmine
class TimeEntryBatchImportSynchronizer(RedmineBatchImportSynchronizer):

    _model_name = 'redmine.hr.analytic.timesheet'

    def run(self, filters=None, options=None):
        """ Run the synchronization """
        if options is None:
            options = {}

        updated_from = datetime.strptime(
            self.backend_record.time_entry_last_update,
            DEFAULT_SERVER_DATETIME_FORMAT)

        if options.get('single_user', False):
            func = import_record

            login = filters.pop('login')
            user_id = self.backend_adapter.search_user(login)
            filters['user_id'] = user_id

        else:
            func = import_record.delay

        record_ids = self.backend_adapter.search(
            updated_from, filters)

        session = self.session
        model_name = self._model_name
        backend_id = self.backend_record.id

        for record_id in record_ids:
            func(session, model_name, backend_id, record_id, options=options)


@redmine
class TimeEntryImportSynchronizer(RedmineImportSynchronizer):

    _model_name = 'redmine.hr.analytic.timesheet'

    def run(self, record_id, options=None):
        """
        Update the last synchronization date on the backend record

        The schedule date of the import batch in Odoo can not be
        used because the time zone can be different in both systems.

        Each time a batch is imported, we take the record with the
        highest value for updated_on.
        """
        if options is None:
            options = {}

        super(TimeEntryImportSynchronizer, self).run(record_id)

        backend = self.backend_record

        if (
            self.updated_on > backend.time_entry_last_update and
            not options.get('single_user', False)
        ):
            backend.write({'time_entry_last_update': self.updated_on})


def import_single_user_time_entries(
    session, backend_id, login, date_from, date_to
):
    """ Import time entries for a single user """
    env = get_environment(session, 'redmine.hr.analytic.timesheet', backend_id)
    importer = env.get_connector_unit(RedmineBatchImportSynchronizer)

    filters = {
        'login': login,
        'from_date': date_from,
        'to_date': date_to,
    }

    try:
        importer.run(filters=filters, options={'single_user': True})
    except ConnectorException as err:
        raise orm.except_orm(
            _('Error !'),
            _("An error was encountered while importing timesheets from "
                "Redmine: %s") % ustr(err))
