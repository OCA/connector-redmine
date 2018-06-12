# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo.addons.connector.exception import MappingError
from odoo.addons.component.core import Component

from datetime import datetime


class TimeEntryBatchImportSynchronizer(Component):

    _name = 'redmine.account.analytic.line.batch.importer'
    _inherit = 'redmine.importer'
    _usage = 'batch.importer'
    _apply_on = 'redmine.account.analytic.line'

    def _import_record(self, external_id):
        """ Delay the import of the records"""
        delayable = self.model.with_delay()
        delayable.import_record(self.backend_record, external_id)

    def run(self, filters=None, options=None):
        """
        Run the synchronization for all users, using the connector crons.
        """
        updated_from = datetime.strptime(
            self.backend_record.time_entry_last_update,
            DEFAULT_SERVER_DATETIME_FORMAT)

        record_ids = self.backend_adapter.search(
            updated_from, filters)

        for record_id in record_ids:
            self._import_record(record_id)

    def run_single_user(self, filters=None, options=None):
        """
        Run the synchronization for a single user without using the
        connector crons.

        All entries with mapping error will be returned in a list
        so that the user is notified. This prevents blocking the
        import of every timesheets when, for instance, a project
        in redmine is not correctly mapped to an analytic account
        in Odoo.

        :return: list of mapping errors
        """
        if options is None:
            options = {}

        options['single_user'] = True

        updated_from = datetime.strptime(
            self.backend_record.time_entry_last_update,
            DEFAULT_SERVER_DATETIME_FORMAT)

        login = filters.pop('login')
        user_id = self.backend_adapter.search_user(login)
        filters['user_id'] = user_id

        record_ids = self.backend_adapter.search(
            updated_from, filters)

        mapping_errors = []

        for record_id in record_ids:
            try:
                self._import_record(record_id)
            except MappingError as err:
                mapping_errors.append(err)

        return mapping_errors


class TimeEntryBatchDeleterSynchronizer(Component):

    _name = 'redmine.account.analytic.line.batch.deleter'
    _inherit = 'redmine.importer'
    _usage = 'batch.deleter'
    _apply_on = 'redmine.account.analytic.line'

    def get_all_records(self, filters=None):
        return self.backend_adapter.search(None, filters)


class TimeEntryImportSynchronizer(Component):

    _name = 'redmine.account.analytic.line.importer'
    _inherit = 'redmine.importer'
    _usage = 'record.importer'
    _apply_on = 'redmine.account.analytic.line'

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
