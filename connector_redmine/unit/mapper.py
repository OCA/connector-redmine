# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo import fields
from odoo.addons.connector.unit.mapper import mapping
from odoo.addons.component.core import AbstractComponent


class RedmineImportMapper(AbstractComponent):
    _name = 'redmine.import.mapper'
    _inherit = 'base.import.mapper'
    _usage = 'import.mapper'

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def updated_on(self, record):
        date = record['updated_on']
        return {'updated_on': fields.Datetime.to_string(date)}

    @mapping
    def sync_date(self, record):
        date = datetime.now()
        return {'sync_date': fields.Datetime.to_string(date)}
