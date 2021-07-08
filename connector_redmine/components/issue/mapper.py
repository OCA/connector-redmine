# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError
from odoo.tools.translate import _
from textile import textile

_logger = logging.getLogger(__name__)


class RedmineIssueImportMapper(Component):
    _name = "redmine.issue.mapper"
    _inherit = "redmine.import.mapper"
    _apply_on = "redmine.issue"

    direct = [
        ("issue_id", "redmine_id"),
    ]

    children = [("time_entries", "timesheet_ids", "redmine.account.analytic.line")]

    def _map_child(self, map_record, from_attr, to_attr, model_name):
        issue_id = map_record.source["issue_id"]
        child_records = map_record.source[from_attr]
        # Use the adapter read method to get info about user_login and contract_ref
        adapter = self.component(usage="backend.adapter", model_name=model_name)
        # In Redmine a parent issue can have several child-issues,
        # which can have several time entries. The children's time
        # entries are also connected with the parent issue.
        # If the time entries do not belong to the current issue
        # (but to a child), they should not be processed.
        detail_records = [
            adapter.read(child_record.id)
            for child_record in child_records
            if child_record.issue.id == issue_id
        ]
        mapper_child = self._get_map_child_component(model_name)
        items = mapper_child.get_items(
            detail_records, map_record, to_attr, options=self.options
        )
        return items

    @mapping
    def child_ids(self, record):
        issue = record["issue"]
        children = issue.children if hasattr(issue, "children") else []
        issue_binder = self.binder_for("redmine.issue")
        redmine_issue_children = []
        for child in children:
            redmine_issue_child = issue_binder.to_internal(child.id)
            if redmine_issue_child:
                redmine_issue_children.append(redmine_issue_child.odoo_id.id)
        return {"child_ids": [(6, 0, redmine_issue_children)]}

    @mapping
    def date_deadline(self, record):
        issue = record["issue"]
        return {
            "date_deadline": issue.due_date if hasattr(issue, "due_date") else False
        }

    @mapping
    def description(self, record):
        html = textile(record["issue"].description)
        html = html.replace("<table>", '<table border="1">')
        html = html.replace("</table>", "</table><br>")
        return {"description": html}

    @mapping
    def last_update(self, record):
        return {"last_update": record["updated_on"]}

    @mapping
    def name(self, record):
        res = {"name": "#" + str(record["issue_id"]) + " - " + record["issue"].subject}
        return res

    @mapping
    def parent_id(self, record):
        issue = record["issue"]
        parent = issue.parent if hasattr(issue, "parent") else False
        redmine_issue = (
            self.binder_for("redmine.issue").to_internal(parent.id) if parent else False
        )
        return {"parent_id": redmine_issue.odoo_id.id if redmine_issue else False}

    @mapping
    def planned_hours(self, record):
        issue = record["issue"]
        return {
            "planned_hours": issue.estimated_hours
            if hasattr(issue, "estimated_hours")
            else 0
        }

    @mapping
    def priority(self, record):
        issue = record["issue"]
        priority = "0"
        if str(issue.priority) == "Normal":
            priority = "1"
        elif str(issue.priority) == "High":
            priority = "2"
        elif str(issue.priority) == "Urgent":
            priority = "4"
        elif str(issue.priority) == "Immediately":
            priority = "5"
        return {"priority": priority if hasattr(issue, "priority") else 0}

    @mapping
    def progress(self, record):
        # if ('issue' not in record):
        #     import wdb; wdb.set_trace()
        issue = record["issue"]
        return {
            "progress": record["issue"].done_ratio
            if hasattr(issue, "done_ratio")
            else 0
        }

    @mapping
    def project_id(self, record):
        projects = self.env["project.project"].search(
            [
                ("name", "=", record["contract_ref"]),
            ]
        )
        if not projects:
            raise MappingError(
                _("No Odoo project with name '%s' exists.") % record["contract_ref"]
            )
        if len(projects) > 1:
            raise MappingError(
                _("There are more Odoo projects with name '%s'.")
                % record["contract_ref"]
            )
        return {"project_id": projects[0].id}

    @mapping
    def redmine_issue_url(self, record):
        return {"redmine_issue_url": record["issue"].url}

    @mapping
    def stage_id(self, record):
        redmine_issue_status = record["issue"].status
        project_id = self.project_id(record)["project_id"]
        project_name = record["contract_ref"]

        task_type = self.env["project.task.type"].search(
            [
                ("project_ids", "=", project_id),
                ("redmine_issue_state", "=", redmine_issue_status),
            ]
        )
        if len(task_type) == 0:
            raise MappingError(
                _(
                    "There is no project task type for the given project '%s' "
                    "that matches the Redmine state '%s'.\n"
                    "Add the Redmine state to an existing project task type or "
                    "create a new one.\n"
                    "Make also sure that the task type is available for this project."
                )
                % (project_name, redmine_issue_status)
            )
        elif len(task_type) > 1:
            raise MappingError(
                _(
                    "There are more project task types for the given project '%s' "
                    "that match the Redmine state '%s'.\n"
                    "Check for example these types: '%s' and '%s'."
                )
                % (
                    project_name,
                    redmine_issue_status,
                    task_type[0].name,
                    task_type[1].name,
                )
            )
        return {"stage_id": task_type[0].id}

    @mapping
    def user_id(self, record):
        user_obj = self.env["res.users"]
        user = None

        login = record["assigned_user_login"] if "assigned_user_login" in record else ""
        name = (
            record["assigned_user"].name
            if "assigned_user" in record and record["assigned_user"]
            else ""
        )

        if login:
            user = user_obj.search([("login", "=", login)])

        if not user:
            user = user_obj.search([("name", "=", name)])

            if not user:
                project_id = self.project_id(record)["project_id"]
                user = (
                    self.env["project.project"].browse(project_id).default_redmine_user
                )

        if len(user) > 1:
            raise MappingError(
                _(
                    "There is more than one user in Odoo with login name: '%s' or name: '%s'."
                )
                % (login, name)
            )

        return {
            "user_id": user.id if user else None,
            "redmine_user": name,
        }

    def finalize(self, map_record, values):
        """
        For Redmine issues without estimated hours the planned hours in Odoo
        are computed by total spent time from time entries and issue's progress value.
        If the latter is also not set in Redmine, it is interpreted as 5% progress.
        """
        if not values["planned_hours"]:
            spent_hours = map_record.source["issue"].spent_hours
            if not values["progress"] and spent_hours:
                values["progress"] = 5.0
            if values["progress"]:
                values["planned_hours"] = 100 * spent_hours / values["progress"]
        return values
