# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError, Warning
from odoo.tools.misc import ustr
from odoo.tools.translate import _


class RedmineBackend(models.Model):
    _name = "redmine.backend"
    _description = "Redmine Backend"
    _inherit = "connector.backend"
    _rec_name = "location"

    def _select_versions(self):
        return [("1.3", _("1.3 and higher"))]

    location = fields.Char(
        "Location",
        size=128,
        required=True,
    )
    key = fields.Char(
        "Key",
        size=64,
        required=True,
        groups="connector.group_connector_manager",
    )
    version = fields.Selection(_select_versions, string="Version", required=True)
    proxy = fields.Char(
        "Proxy",
        size=128,
        required=False,
    )
    verify_ssl = fields.Boolean(
        "Verify SSL",
        default=True,
    )

    name = fields.Char("Name")

    contract_ref = fields.Char(
        string="Redmine Project Identification",
        help="This is the name of the field added in Redmine used to relate "
        "a Redmine project to an Odoo project.\n"
        "Each Redmine project must have an unique value for this attribute.",
    )

    @api.multi
    def check_auth(self):
        """
        Check the authentication with Redmine
        """
        self.ensure_one()
        with self.work_on("redmine.backend") as work:
            adapter = work.component(usage="backend.adapter")

        try:
            adapter._auth()
        except Exception:
            raise Warning(_("Could not connect to Redmine."))

        raise Warning(
            _("Connection test succeeded. " "Everything seems properly set up.")
        )

    @api.multi
    def check_contract_ref(self):
        """
        Check if the contract_ref field exists in Redmine.
        """
        self.ensure_one()
        with self.work_on("redmine.backend") as work:
            adapter = work.component(usage="backend.adapter")
        try:
            adapter._auth()
        except Exception as e:
            raise UserError(_("Connection to Redmine failed: %s") % ustr(e))

        projects = adapter.redmine_api.project.all()
        exist = False
        assigned = False

        if projects:
            if hasattr(projects[0], "custom_fields"):
                for cs in projects[0].custom_fields:
                    if cs["name"] == self.contract_ref:
                        exist = True
                        assigned = bool(cs["value"])
            elif hasattr(projects[0], self.contract_ref):
                exist = True

        if not exist:
            raise UserError(
                _(
                    "Redmine backend configuration error:\n"
                    "The Redmine project identification name doesn't exist."
                )
            )
        elif not assigned:
            raise UserError(
                _(
                    "Redmine backend configuration error:\n"
                    "The Redmine project identification field is not assigned in Redmine."
                )
            )
        else:
            raise UserError(
                _("Connection test succeeded. Everything seems properly set up.")
            )
