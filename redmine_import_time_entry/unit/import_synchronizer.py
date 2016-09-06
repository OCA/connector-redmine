# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, ustr
from openerp.tools.translate import _

from openerp.addons.connector.exception import ConnectorException

from openerp.addons.connector_redmine.backend import redmine
from openerp.addons.connector_redmine.connector import get_environment
from openerp.addons.connector_redmine.unit.import_synchronizer import (
    RedmineBatchImportSynchronizer, RedmineImportSynchronizer,
    import_record)
from openerp.addons.connector.exception import MappingError

from datetime import datetime


@redmine
class TimeEntryBatchImportSynchronizer(RedmineBatchImportSynchronizer):

    _model_name = 'redmine.hr.analytic.timesheet'

    def run(self, filters=None, options=None):
        """
        Run the synchronization for all users, using the connector crons.
        """
        updated_from = datetime.strptime(
            self.backend_record.time_entry_last_update,
            DEFAULT_SERVER_DATETIME_FORMAT)

        record_ids = self.backend_adapter.search(
            updated_from, filters)

        session = self.session
        model_name = self._model_name
        backend_id = self.backend_record.id

        for record_id in record_ids:
            import_record.delay(
                session, model_name, backend_id, record_id, options=options)

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

        session = self.session
        model_name = self._model_name
        backend_id = self.backend_record.id

        mapping_errors = []

        for record_id in record_ids:
            try:
                import_record(
                    session, model_name, backend_id,
                    record_id, options=options)

            except MappingError as err:
                mapping_errors.append(err)

        return mapping_errors


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
        return importer.run_single_user(filters=filters)
    except ConnectorException as err:
        raise ValidationError(
            _("An error was encountered while importing timesheets from "
                "Redmine: %s") % ustr(err))
