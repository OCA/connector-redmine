# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    redmine_time_entry_id = fields.Integer(string="Redmine ID")

    last_update = fields.Datetime(
        string="Last updated on",
        help="During last issue import this was the date and time "
        "this time entry was last updated in Redmine.",
    )
