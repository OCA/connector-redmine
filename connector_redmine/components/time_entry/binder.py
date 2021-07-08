# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class RedmineTimeEntryBinder(Component):
    _name = "redmine.account.analytic.line.binder"
    _inherit = "redmine.binder"
    _apply_on = "redmine.account.analytic.line"
