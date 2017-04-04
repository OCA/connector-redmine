# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, ustr
from odoo.fields import Datetime
from odoo.addons.connector.connector import Binder
from ..backend import redmine


@redmine
class RedmineModelBinder(Binder):
    _model_name = [
        'redmine.account.analytic.line',
    ]
    _external_field = 'redmine_id'
    _backend_field = 'backend_id'
    _odoo_field = 'odoo_id'
    _sync_date_field = 'sync_date'

    def bind(self, external_id, binding):
        """ Create the link between an external ID and an Odoo ID and
        update the last synchronization date.

        :param external_id: External ID to bind
        :param binding_id: Odoo ID to bind
        :type binding_id: int
        """
        # TODO: Check whether DEFAULT_SERVER_DATETIME_FORMAT is still needed
        # or just inherited from the past. It is not being used in base method.
        # Otherwise the method can be erased and the inherited one would fit.
        # Prevent False, None, or "", but not 0
        assert (external_id or external_id is 0) and binding, (
            "external_id or binding missing, "
            "got: %s, %s" % (external_id, binding)
        )
        # avoid to trigger the export when we modify the `external_id`
        now_fmt = Datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if isinstance(binding, models.BaseModel):
            binding.ensure_one()
        else:
            binding = self.model.browse(binding)
        binding.with_context(connector_no_export=True).write(
            {self._external_field: ustr(external_id),
             self._sync_date_field: now_fmt,
             })
