# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class BackendAdapter(Component):

    _name = "redmine.backend.adapter"
    _inherit = "redmine.adapter"
    _apply_on = "redmine.backend"
