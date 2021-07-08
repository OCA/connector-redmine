# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class Project(models.Model):
    _inherit = "project.project"

    default_redmine_user = fields.Many2one(
        string="Default Redmine User",
        comodel_name="res.users",
        help="This is the user who will be set to tasks and account "
        "analytic lines if the Redmine user does not match any "
        "Odoo user, when importing issues from Redmine.",
    )

    last_imported_on = fields.Datetime(
        string="Last imported on",
        help="During last issue import this was the date "
        "and time of the last updated issue.",
    )

    redmine_project_url = fields.Char(string="Redmine Project")

    @api.multi
    def import_issues_from_redmine(self):
        """
        Call the connector to import Redmine issues for a project.
        If mapping errors occur, post a comment below project.
        """
        self.check_access_rule("write")

        backend = self.get_project_backend()

        last_imported_on = None
        if self.last_imported_on:
            lst_on = datetime.strftime(
                self.last_imported_on, DEFAULT_SERVER_DATETIME_FORMAT
            )  # port to v12
            last_imported_on = datetime.strptime(lst_on, DEFAULT_SERVER_DATETIME_FORMAT)

        with backend.work_on("redmine.issue") as work:
            importer = work.component(usage="batch.importer")
            mapping_errors = importer.run_single_project(
                project_name=self.name,
                project_url=self.redmine_project_url,
                last_imported_on=last_imported_on,
            )

        # TODO: Collect all mapping errors and post them on project
        if mapping_errors:
            part_1 = _("Some issues were not imported from Redmine.")
            part_2 = "\n".join({e.message for e in mapping_errors})
            body = "%s\n%s" % (part_1, part_2)

            # Log the message using SUPERUSER_ID, because otherwise
            # the user will not be notified by email and might see
            # that some entries were not imported.
            self.sudo().message_post(
                body=body,
                type="comment",
                subtype="mail.mt_comment",
                content_subtype="plaintext",
            )

    def get_project_backend(self):
        """
        Redmine project URLs look like this: http://redmine.url/projects/projectname
        The Redmine backend location is this URL without further paths: http://redmine.url/
        :return: redmine backend object
        """
        url = self.redmine_project_url.split("projects")[0]

        backend = (
            self.env["redmine.backend"]
            .sudo()
            .search(["|", ("location", "=", url), ("location", "=", url[:-1])])
        )

        if not backend:
            raise ValidationError(
                _("No Redmine backend configured that has this location: %s.") % url
            )

        return backend

    @api.model
    def _run_import_issues(self):
        """ This method is called from a cron job. """
        projects = self.search([("redmine_project_url", "!=", False)])
        if projects:
            for project in projects:
                project.import_issues_from_redmine()


class ProjectTask(models.Model):
    _inherit = "project.task"

    last_update = fields.Datetime(
        string="Last updated on",
        help="During last issue import this was the date and "
        "time this issue was last updated in Redmine.",
    )

    # planned hours is either directly imported from Redmine
    # or computed in finalize step of mapping
    planned_hours = fields.Float(string="Initially Planned Hours")

    # progress is imported from Redmine, not computed anymore
    progress = fields.Float(string="Working Time Recorded", compute=False)

    redmine_issue_url = fields.Char(string="Redmine Issue", readonly=True)

    redmine_user = fields.Char(
        string="Redmine User",
        help="This is the name of the assigned Redmine User. "
        "It is set, if the Redmine user is no Odoo user.",
    )

    user_id = fields.Many2one(track_visibility=False)
    priority = fields.Selection(selection_add=[("4", "Urgent"), ("5", "Immediately")])

    @api.constrains("parent_id", "child_ids")
    def _check_subtask_level(self):
        """
        Since Odoo 12 it is not allowed to have multi-level task hierarchy.
        We want it though. So, no contrain for parent_id and child_ids needed.
        """
        pass

    @api.depends("child_ids")
    def _compute_subtask_count(self):
        """
        Since Odoo 12 it is not allowed to have multi-level task hierarchy.
        We want it though. So, the read_group-method cannot be used here.
        The calculation method from Odoo 11 is used again.
        """
        for task in self:
            task.subtask_count = self.search_count(
                [("id", "child_of", task.id), ("id", "!=", task.id)]
            )


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    redmine_issue_state = fields.Char(
        string="Redmine Issue State",
        help="Please enter which Redmine Issue-State shall "
        "be mapped to this task type.",
    )
