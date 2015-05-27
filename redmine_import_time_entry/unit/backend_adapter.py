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

    def read(self, redmine_id):
        self._auth()

        try:
            entry = self.redmine_api.time_entry.get(redmine_id)
        except exceptions.ResourceNotFoundError:
            return None

        issue = 'issue' in dir(entry) and self.redmine_api.issue.get(
            entry.issue.id)

        project = self.redmine_api.project.get(entry.project.id)

        custom_field = self.backend_record.contract_ref

        contract_ref = next((
            field.value for field in project.custom_fields
            if field.name == custom_field), False)

        if not contract_ref:
            raise InvalidDataError(
                _('The field %s is not set in Redmine for project %s ') %
                (custom_field, project.name))

        user = self.redmine_api.user.get(entry.user.id)

        return {
            'entry_id': entry.id,
            'spent_on': entry.spent_on,
            'hours': entry.hours,
            'issue_id': issue and issue.id,
            'issue_subject': issue and issue.subject,
            'contract_ref': contract_ref,
            'project_name': project.name,
            'project_id': project.id,
            'updated_on': entry.updated_on,
            'user_login': user.login,
        }
