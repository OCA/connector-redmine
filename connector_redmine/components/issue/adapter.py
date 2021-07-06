# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

import odoo.addons.connector.exception as cn_exception
from odoo.addons.component.core import Component
from odoo.tools.translate import _
from redminelib import exceptions

_logger = logging.getLogger(__name__)


class RedmineIssueAdapter(Component):
    _name = "redmine.issue.adapter"
    _inherit = "redmine.adapter"
    _apply_on = "redmine.issue"
    _collection = "redmine.backend"

    def search(self, project_name, project_url, last_imported_on=None):
        """
        Get all issues filtered by project or those currently updated or
        whose time entries were currently updated.
        :param project_name: string containing the project's name in Odoo
        :param project_url: string containing the project's url
        :param last_imported_on: datetime with time of last imported record
        :return:
        """
        self._auth()

        redmine_project_id = self._get_redmine_project(project_name, project_url)

        if last_imported_on:
            issues = []
            for issue in self.redmine_api.issue.all():
                if issue.project.id == redmine_project_id:
                    if last_imported_on < issue.updated_on:
                        issues.append(issue.id)
                    else:
                        for time_entry in issue.time_entries:
                            if last_imported_on < time_entry.updated_on:
                                issues.append(issue.id)
                                break
            return issues
        else:
            return [
                issue.id
                for issue in self.redmine_api.issue.all()
                if issue.project.id == redmine_project_id
            ]

    def _get_redmine_project(self, project_name, project_url):
        """
        Get project id of redmine project by its Odoo name or its URL.
        :param project_name: string containing the project's name in Odoo
        :param project_url: string containing the project's url
        :return: integer id of found redmine project
        """
        redmine_project_ids = []
        for project in self.redmine_api.project.all():
            if hasattr(project, "custom_fields"):
                for field in project.custom_fields:
                    if hasattr(field, "name") and hasattr(field, "value"):
                        if (
                            field.name == self.backend_record.contract_ref
                            and field.value == project_name
                        ):
                            redmine_project_ids.append(project.id)
            else:
                if not project_url:
                    raise Exception(
                        _(
                            "There is no Redmine project URL given to identify correct redmine project."
                        )
                    )
                # URLs in Redmine api are stored without appended '/'
                if project_url[-1] == "/":
                    project_url = project_url[:-1]

                if project.url == project_url:
                    redmine_project_ids.append(project.id)

        if not redmine_project_ids:
            raise Exception(
                _(
                    "There is no Redmine project with given name: '%s' or URL: '%s'."
                    % (project_name, project_url)
                )
            )
        if len(redmine_project_ids) > 1:
            raise Exception(
                _(
                    "There is more than one Redmine project with given name: '%s' or URL: '%s'."
                    % (project_name, project_url)
                )
            )

        return redmine_project_ids[0]

    def read(self, record_id):
        self._auth()

        try:
            issue = self.redmine_api.issue.get(record_id)
        except exceptions.ResourceNotFoundError:
            return None
        except exceptions.ForbiddenError:
            return None

        project = self.redmine_api.project.get(issue.project.id)
        custom_field = self.backend_record.contract_ref

        if hasattr(project, "custom_fields"):
            contract_ref = next(
                (
                    field.value
                    for field in project.custom_fields
                    if field.name == custom_field
                ),
                False,
            )
        elif hasattr(project, self.backend_record.contract_ref):
            contract_ref = getattr(project, self.backend_record.contract_ref)

        if not contract_ref:
            raise cn_exception.InvalidDataError(
                _("The field %(field)s is not set in Redmine for project %(project)s.")
                % {
                    "field": custom_field,
                    "project": project.name,
                }
            )

        user = issue.assigned_to if hasattr(issue, "assigned_to") else False

        try:
            user = self.redmine_api.user.get(user.id) if user else False
        except exceptions.ResourceNotFoundError:
            _logger.warning(
                _("Redmine-Issue: %s - The user %s does not exist in Redmine anymore.")
                % (issue.id, user.name if user else "")
            )

        user_login = user.login if hasattr(user, "login") else ""

        res = {
            "project": project,
            "contract_ref": contract_ref,
            "issue": issue,
            "issue_id": issue.id,
            "updated_on": issue.updated_on,
            "assigned_user": issue.assigned_to
            if hasattr(issue, "assigned_to")
            else False,
            "assigned_user_login": user_login,
            "time_entries": issue.time_entries,
        }
        return res
