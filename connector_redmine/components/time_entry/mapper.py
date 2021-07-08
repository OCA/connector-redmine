# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class RedmineTimeEntryImportMapper(Component):
    _name = "redmine.account.analytic.line.mapper"
    _inherit = "redmine.import.mapper"
    _apply_on = "redmine.account.analytic.line"

    direct = [
        ("entry_id", "redmine_id"),
    ]

    @mapping
    def date(self, record):
        return {"date": record["time_entry"].spent_on}

    @mapping
    def last_update(self, record):
        return {"last_update": record["updated_on"]}

    @mapping
    def name(self, record):
        time_entry = record["time_entry"]
        comment = "[#" + str(time_entry.issue.id)
        comment += (
            " - " + time_entry.activity.name if hasattr(time_entry, "activity") else ""
        )
        comment += "] "
        if hasattr(time_entry, "comments"):
            # if isinstance(time_entry.comments, unicode):
            # 'unicode' to 'str' for port to v12
            if isinstance(time_entry.comments, str):
                comment += time_entry.comments
            else:
                comment += str(time_entry.comments)
        return {"name": comment}

    @mapping
    def project_id(self, record):
        project = self.env["project.project"].search(
            [
                ("name", "=", record["contract_ref"]),
            ]
        )
        if not project:
            raise MappingError(
                _("No Odoo project with name '%s' exists.") % record["contract_ref"]
            )
        if len(project) > 1:
            raise MappingError(
                _("There are more Odoo projects with name '%s'.")
                % record["contract_ref"]
            )
        res = {
            "project_id": project.id,
            "account_id": project.analytic_account_id.id,
        }
        return res

    @mapping
    def redmine_time_entry_id(self, record):
        return {"redmine_time_entry_id": record["entry_id"]}

    @mapping
    def task_id(self, record):
        time_entry = record["time_entry"]
        issue = time_entry.issue
        issue_binder = self.binder_for("redmine.issue")
        issue_binding = issue_binder.to_internal(issue.id)
        res = {
            "task_id": issue_binding.odoo_id.id if issue_binding else False,
            'issue_id': issue_binding.id if issue_binding else False,
        }
        return res

    @mapping
    def unit_amount(self, record):
        return {"unit_amount": record["time_entry"].hours}

    @mapping
    def user_id(self, record):
        user_obj = self.env["res.users"]
        user = None

        login = record["user_login"] if "user_login" in record else ""
        name = record["user"].name if "user" in record else ""

        if login:
            user = user_obj.search([("login", "=", login)])

        if not user:
            user = user_obj.search([("name", "=", name)])

            if not user:
                _logger.warning(
                    _(
                        "There is no user in Odoo with login name: '%s' or name: '%s'.\n"
                        "The project's default user will be set for the time entry."
                    )
                    % (login, name)
                )

                project_id = self.project_id(record)["project_id"]
                user = (
                    self.env["project.project"].browse(project_id).default_redmine_user
                )

                if not user:
                    raise MappingError(
                        _(
                            "There is no user in Odoo with login name: '%s' or name: '%s'.\n"
                            "And there is also no default Redmine user set for this project."
                        )
                        % (login, name)
                    )

        if len(user) > 1:
            raise MappingError(
                _(
                    "There is more than one user in Odoo with login name: '%s' or name: '%s'."
                )
                % (login, name)
            )
        return {"user_id": user.id}
