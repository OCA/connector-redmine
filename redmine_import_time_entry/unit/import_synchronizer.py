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

from openerp.addons.connector_redmine.backend import redmine13
from openerp.addons.connector_redmine.unit.import_synchronizer import (
    RedmineBatchImportSynchronizer, RedmineImportSynchronizer,
    import_record)
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime


@redmine13
class TimeEntryBatchImportSynchronizer(RedmineBatchImportSynchronizer):

    _model_name = 'redmine.hr.analytic.timesheet'

    def run(self, filters=None):
        """ Run the synchronization """
        updated_from = datetime.strptime(
            self.backend_record.time_entry_last_update,
            DEFAULT_SERVER_DATETIME_FORMAT)

        record_ids = self.backend_adapter.search(
            updated_from, filters)

        for record_id in record_ids:
            import_record.delay(
                self.session, self._model_name, self.backend_record.id,
                record_id)


@redmine13
class TimeEntryImportSynchronizer(RedmineImportSynchronizer):

    _model_name = 'redmine.hr.analytic.timesheet'

    def run(self, record_id):
        """
        Update the last synchronization date on the backend record

        The schedule date of the import batch in Odoo can not be
        used because the time zone can be different in both systems.

        Each time a batch is imported, we take the record with the
        highest value for updated_on.
        """
        super(TimeEntryImportSynchronizer, self).run(record_id)

        backend = self.backend_record
        if self.updated_on > backend.time_entry_last_update:
            backend.write({'time_entry_last_update': self.updated_on})
