# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class RedmineIssueBinder(Component):
    _name = "redmine.issue.binder"
    _inherit = "redmine.binder"
    _apply_on = "redmine.issue"
