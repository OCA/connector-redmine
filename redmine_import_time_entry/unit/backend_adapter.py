# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tools.translate import _
from openerp.addons.connector.exception import InvalidDataError
from redmine import exceptions
from openerp.addons.connector_redmine.unit.backend_adapter import (
    RedmineAdapter)
from openerp.addons.connector_redmine.backend import redmine


@redmine
class TimeEntryAdapter(RedmineAdapter):
    """
    Time Entry Backend Adapter for Redmine

    Time entries in Redmine can not be querried by the date of creation
    or update. The alternative is to search for all entries for a
    period of time and then filtering these by the field updated_on.
    """

    _model_name = 'redmine.hr.analytic.timesheet'

    def search(self, updated_from, filters):
        """
        Get all time entry that were updated between the interval of time
        """
        self._auth()

        if updated_from:
            return [
                entry.id for entry in
                self.redmine_api.time_entry.filter(**filters)
                if updated_from < entry.updated_on
            ]
        else:
            # If the time entries are imported for the first time
            # no need to filter by the date of update
            return [
                entry.id for entry in
                self.redmine_api.time_entry.filter(**filters)
            ]

    def get_project(self, project_id):
        project_cache = self.session.redmine_cache['project']
        if project_id not in project_cache:
            project = self.redmine_api.project.get(project_id)
            project_cache[project_id] = project
        return project_cache[project_id]

    def get_issue(self, issue_id):
        issue_cache = self.session.redmine_cache['issue']
        if issue_id not in issue_cache:
            issue = self.redmine_api.issue.get(issue_id)
            issue_cache[issue_id] = issue
        return issue_cache[issue_id]

    def read(self, redmine_id):
        self._auth()

        try:
            entry = self.redmine_api.time_entry.get(redmine_id)
        except exceptions.ResourceNotFoundError:
            return None

        issue = 'issue' in dir(entry) and self.get_issue(entry.issue.id)
        project = self.get_project(entry.project.id)

        custom_field = self.backend_record.contract_ref

        contract_ref = next((
            field.value for field in project.custom_fields
            if field.name == custom_field), False)

        if not contract_ref:
            raise InvalidDataError(
                _('The field %(field)s is not set in Redmine for project '
                    '%(project)s.') % {
                    'field': custom_field,
                    'project': project.name
                })

        user = self.redmine_api.user.get(entry.user.id)

        return {
            'entry_id': long(entry.id),
            'spent_on': entry.spent_on,
            'hours': entry.hours,
            'issue_id': issue and long(issue.id),
            'issue_subject': issue and issue.subject,
            'contract_ref': contract_ref,
            'project_name': project.name,
            'project_id': long(project.id),
            'updated_on': entry.updated_on,
            'user_login': user.login,
        }
