# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tools.translate import _
import odoo.addons.connector.exception as cn_exception
from redminelib import exceptions
from odoo.addons.component.core import Component


class TimeEntryAdapter(Component):
    """
    Time Entry Backend Adapter for Redmine

    Time entries in Redmine can not be querried by the date of creation
    or update. The alternative is to search for all entries for a
    period of time and then filtering these by the field updated_on.
    """

    _name = 'redmine.account.analytic.line.adapter'
    _inherit = 'redmine.adapter'
    _apply_on = 'redmine.account.analytic.line'
    _collection = 'redmine.backend'

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
        project = self.redmine_api.project.get(project_id)
        return project

    def get_issue(self, issue_id):
        issue = self.redmine_api.issue.get(issue_id)
        return issue

    def read(self, redmine_id):
        self._auth()

        try:
            entry = self.redmine_api.time_entry.get(redmine_id)
        except exceptions.ResourceNotFoundError:
            return None
        except exceptions.ForbiddenError:
            return None

        issue = 'issue' in dir(entry) and self.get_issue(entry.issue.id)
        project = self.get_project(entry.project.id)

        custom_field = self.backend_record.contract_ref

        if hasattr(project, 'custom_fields'):
            contract_ref = next((
                field.value for field in project.custom_fields
                if field.name == custom_field), False)
        elif hasattr(project, self.backend_record.contract_ref):
            contract_ref = getattr(project, self.backend_record.contract_ref)

        if not contract_ref:
            raise cn_exception.InvalidDataError(
                _('The field %(field)s is not set in Redmine for project '
                    '%(project)s.') % {
                    'field': custom_field,
                    'project': project.name
                })

        res = {
            'entry_id': long(entry.id),
            'spent_on': entry.spent_on,
            'hours': entry.hours,
            'issue_id': issue and long(issue.id),
            'issue_subject': issue and issue.subject,
            'contract_ref': contract_ref,
            'project_name': project.name,
            'project_id': long(project.id),
            'updated_on': entry.updated_on,
            'comments': entry.comments,
        }

        if self.backend_record.sync_tasks:
            res['version'] = issue.version

        user = self.redmine_api.user.get(entry.user.id)
        if hasattr(user, 'login'):
            res['user_login'] = user.login
        elif hasattr(user, 'firstname') and hasattr(user, 'lastname'):
            res['user_name'] = '%s %s' % (user.firstname, user.lastname)
        else:
            raise Exception("Can't find user login nor firstname nor lastname")

        return res
