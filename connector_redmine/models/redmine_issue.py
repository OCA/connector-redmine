# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models
from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)


class RedmineIssue(models.Model):
    _name = "redmine.issue"
    _description = "Redmine Issue Binding"
    _inherit = "redmine.binding"
    _inherits = {"project.task": "odoo_id"}

    odoo_id = fields.Many2one(
        string="Task", comodel_name="project.task", required=True, ondelete="cascade"
    )

    timesheet_ids = fields.One2many(
        string="Redmine Time Entries",
        comodel_name="redmine.account.analytic.line",
        inverse_name="issue_id",
    )

    @job
    @api.model
    def import_record(self, backend, record_id):
        with backend.work_on(self._name) as work:
            importer = work.component(usage="record.importer")
            return importer.run(record_id)


class RedmineTimeEntry(models.Model):
    _name = "redmine.account.analytic.line"
    _description = "Redmine Time Entry Binding"
    _inherit = "redmine.binding"
    _inherits = {"account.analytic.line": "odoo_id"}

    odoo_id = fields.Many2one(
        string="Timesheet",
        comodel_name="account.analytic.line",
        required=True,
        ondelete="cascade",
    )

    issue_id = fields.Many2one(
        string="Redmine Issue",
        comodel_name="redmine.issue",
        required=True,
        ondelete="cascade",
        index=True,
    )

    @api.model
    def create(self, values):
        """
        Create a time entry binding with reference to odoo task
        if task did not existed before import. If the task already
        existed, it is set during time entry mapping.
        """
        if not values.get("task_id", False):
            redmine_issue = self.env["redmine.issue"].browse(values["issue_id"])
            values["task_id"] = redmine_issue.odoo_id.id
        return super(RedmineTimeEntry, self).create(values)
