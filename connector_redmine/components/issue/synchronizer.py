# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.addons.component.core import Component
from odoo.addons.connector.exception import MappingError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class RedmineIssueBatchImportSynchronizer(Component):
    _name = "redmine.issue.batch.importer"
    _inherit = "redmine.importer"
    _usage = "batch.importer"
    _apply_on = "redmine.issue"

    def _import_record(self, external_id):
        """ Delay the import of the records"""
        delayable = self.model.with_delay()
        delayable.import_record(self.backend_record, external_id)

    def run_single_project(self, project_name, project_url, last_imported_on=None):
        """
        Run Redmine Import without cron jobs.
        :param project_name: string to identify redmine project by its custom field
        :param project_url: string to identify redmine project by its url
        :param filters: dictionary containing redmine fields to filter records
        :param last_imported_on: datetime to get only currently updated records
        :return: list of mapping errors
        """
        record_ids = self.backend_adapter.search(
            project_name=project_name,
            project_url=project_url,
            last_imported_on=last_imported_on,
        )

        # TODO: Collect all mapping errors and post them on project
        mapping_errors = []

        for record_id in record_ids:
            try:
                self._import_record(record_id)
            except MappingError as err:
                mapping_errors.append(err)

        return mapping_errors


class RedmineIssueImportSynchronizer(Component):
    _name = "redmine.issue.importer"
    _inherit = "redmine.importer"
    _apply_on = "redmine.issue"

    def run(self, record_id):
        """
        Update the last synchronization date on the backend record

        The schedule date of the import batch in Odoo can not be
        used because the time zone can be different in both systems.

        Each time a batch is imported, we take the record with the
        highest value for updated_on.
        """
        super(RedmineIssueImportSynchronizer, self).run(record_id)

        project = self.env["project.project"].search(
            [("name", "=", self.redmine_record["contract_ref"])]
        )

        # check also the time_entries for their last updated_on, could be later than the issue updated_on
        updated_on = datetime.strptime(self.updated_on, DEFAULT_SERVER_DATETIME_FORMAT)
        if not project.last_imported_on or updated_on > project.last_imported_on:
            project.write({"last_imported_on": self.updated_on})
