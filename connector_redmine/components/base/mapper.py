# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo import fields
from odoo.addons.component.core import AbstractComponent, Component
from odoo.addons.connector.components.mapper import mapping


class RedmineImportMapper(AbstractComponent):
    _name = "redmine.import.mapper"
    _inherit = "base.import.mapper"
    _usage = "import.mapper"

    @mapping
    def backend_id(self, record):
        return {"backend_id": self.backend_record.id}

    @mapping
    def updated_on(self, record):
        date = record["updated_on"]
        return {"updated_on": fields.Datetime.to_string(date)}

    @mapping
    def sync_date(self, record):
        date = datetime.now()
        return {"sync_date": fields.Datetime.to_string(date)}


class RedmineImportMapChild(Component):
    _name = "redmine.import.child.mapper"
    _inherit = "base.map.child.import"
    _usage = "import.map.child"

    def get_item_values(self, map_record, to_attr, options):
        """ Resolve the ids for updates """
        values = map_record.values(**options)
        binding = self.binder_for().to_internal(values["redmine_id"])
        if binding:
            values["id"] = binding.id
        return values

    def format_items(self, items_values):
        """Updates children when they already exist in the DB"""

        def format_item(values):
            _id = values.pop("id", None)
            return (1, _id, values) if _id else (0, 0, values)

        return [format_item(values) for values in items_values]
