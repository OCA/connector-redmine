# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp.addons.connector.exception import IDMissingInBackend

from odoo.tools.translate import _
from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class RedmineImporter(AbstractComponent):
    """ Base importer for Redmine """
    _name = 'redmine.importer'
    _inherit = ['base.importer', 'base.connector']
    _usage = 'record.importer'

    def __init__(self, work_context):
        """
        :param environment: current environment (backend, ...)
        :type environment: :py:class:`connector.connector.ConnectorEnvironment`
        """
        super(RedmineImporter, self).__init__(work_context)
        self.redmine_id = None
        self.updated_on = None

    def _get_redmine_data(self):
        """ Return the raw Redmine data for ``self.redmine_id`` in a dict
        """
        return self.backend_adapter.read(self.redmine_id)

    def _map_data(self):
        """
        Return an instance of
        :py:class:`~odoo.addons.connector.unit.mapper.MapRecord`
        """
        return self.mapper.map_record(self.redmine_record)

    def _get_binding(self):
        """Return the binding id from the redmine id"""
        return self.binder.to_internal(self.redmine_id)

    def _create_data(self, map_record, **kwargs):
        return map_record.values(for_create=True, **kwargs)

    def _create(self, data):
        """ Create the Odoo record """
        # special check on data before import
        model = self.model.with_context(connector_no_export=True)
        binding = model.create(data)
        _logger.debug('%d created from redmine %s', binding, self.redmine_id)
        return binding

    def _update_data(self, map_record, **kwargs):
        return map_record.values(**kwargs)

    def _update(self, binding, data):
        """ Update an Odoo record """
        # special check on data before import
        binding.with_context(connector_no_export=True).write(data)
        _logger.debug('%d updated from redmine %s', binding, self.redmine_id)
        return

    def run(self, redmine_id):
        """ Run the synchronization

        :param redmine_id: identifier of the record on Redmine
        :param options: dict of parameters used by the synchronizer
        """
        self.redmine_id = redmine_id
        try:
            self.redmine_record = self._get_redmine_data()
        except IDMissingInBackend:
            return _('Record does no longer exist in Redmine')

        # Case where the redmine record is not found in the backend.
        if self.redmine_record is None:
            return

        binding = self._get_binding()

        map_record = self._map_data()
        self.updated_on = map_record.values()['updated_on']

        if binding:
            record = self._update_data(map_record)
            self._update(binding, record)
        else:
            record = self._create_data(map_record)
            binding = self._create(record)

        self.binder.bind(self.redmine_id, binding)
