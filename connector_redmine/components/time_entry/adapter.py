# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

import odoo.addons.connector.exception as cn_exception
from odoo.addons.component.core import Component
from odoo.tools.translate import _
from redminelib import exceptions

_logger = logging.getLogger(__name__)


class RedmineTimeEntryAdapter(Component):
    _name = "redmine.account.analytic.line.adapter"
    _inherit = "redmine.adapter"
    _apply_on = "redmine.account.analytic.line"
    _collection = "redmine.backend"

    def read(self, record_id):
        # super(RedmineTimeEntryAdapter, self).read(record_id)
        self._auth()

        try:
            time_entry = self.redmine_api.time_entry.get(record_id)
        except exceptions.ResourceNotFoundError:
            return None
        except exceptions.ForbiddenError:
            return None

        project = self.redmine_api.project.get(time_entry.project.id)
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
                % {"field": custom_field, "project": project.name}
            )

        user = time_entry.user if hasattr(time_entry, "user") else False

        try:
            user = self.redmine_api.user.get(user.id) if user else False
        except exceptions.ResourceNotFoundError:
            _logger.warning(
                _("Redmine-Issue: %s - The user %s does not exist in Redmine anymore.")
                % (time_entry.issue.id, user.name if user else "")
            )

        user_login = user.login if hasattr(user, "login") else ""

        res = {
            "time_entry": time_entry,
            "entry_id": time_entry.id,
            "entry_hours": time_entry.hours,
            "project": project,
            "contract_ref": contract_ref,
            "updated_on": time_entry.updated_on,
            "user": time_entry.user if hasattr(time_entry, "user") else False,
            "user_login": user_login,
        }
        return res

    def search(self, updated_from, filters):
        """
        Get all time entry that were updated between the interval of time
        """
        self._auth()

        if updated_from:
            return [
                entry.id
                for entry in self.redmine_api.time_entry.filter(**filters)
                if updated_from < entry.updated_on
            ]
        else:
            # If the time entries are imported for the first time
            # no need to filter by the date of update
            return [entry.id for entry in self.redmine_api.time_entry.filter(**filters)]
