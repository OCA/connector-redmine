# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import AbstractComponent


class RedmineModelBinder(AbstractComponent):
    _name = "redmine.binder"
    _inherit = "base.binder"
    _external_field = "redmine_id"
    _backend_field = "backend_id"
    _odoo_field = "odoo_id"
    _sync_date_field = "sync_date"
