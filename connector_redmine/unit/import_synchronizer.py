# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

import logging
from openerp.addons.connector.unit import synchronizer
from openerp.addons.connector.queue.job import job
from ..connector import get_environment

_logger = logging.getLogger(__name__)


class RedmineImportSynchronizer(synchronizer.ImportSynchronizer):
    """ Base importer for Redmine """

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.ConnectorEnvironment`
        """
        super(RedmineImportSynchronizer, self).__init__(environment)
        self.redmine_id = None
        self.updated_on = None
        self._redmine_cache = defaultdict(dict)
        environment._redmine_cache = self._redmine_cache

    def _get_redmine_data(self):
        """ Return the raw Redmine data for ``self.redmine_id`` in a dict
        """
        return self.backend_adapter.read(self.redmine_id)

    def _map_data(self):
        """
        Return an instance of
        :py:class:`~openerp.addons.connector.unit.mapper.MapRecord`
        """
        return self.mapper.map_record(self.redmine_record)

    def _get_binding_id(self):
        """Return the binding id from the redmine id"""
        return self.binder.to_openerp(self.redmine_id)

    def _create_data(self, map_record, **kwargs):
        return map_record.values(for_create=True, **kwargs)

    def _create(self, data):
        """ Create the OpenERP record """
        model = self.session.env[self.model._name]
        binding = model.create(data)

        _logger.info(
            '%s %d created from Redmine %s',
            self.model._name, binding.id, self.redmine_id)

        return binding

    def _update_data(self, map_record, **kwargs):
        return map_record.values(**kwargs)

    def _update(self, binding_id, data):
        """Update an OpenERP record"""
        model = self.session.env[self.model._name]
        record = model.browse(binding_id)
        record.write(data)

        _logger.info(
            '%s %d updated from Redmine record %s',
            self.model._name, binding_id, self.redmine_id)

    def run(self, redmine_id, options=None):
        """ Run the synchronization

        :param redmine_id: identifier of the record on Redmine
        :param options: dict of parameters used by the synchronizer
        """
        self.redmine_id = redmine_id
        self.redmine_record = self._get_redmine_data()

        # Case where the redmine record is not found in the backend.
        if self.redmine_record is None:
            return

        binding_id = self._get_binding_id()

        map_record = self._map_data()
        self.updated_on = map_record.values()['updated_on']

        if binding_id:
            record = self._update_data(map_record)
            self._update(binding_id, record)
        else:
            record = self._create_data(map_record)
            binding_id = self._create(record).id

        self.binder.bind(self.redmine_id, binding_id)


class RedmineBatchImportSynchronizer(synchronizer.ImportSynchronizer):
    def run(self, filters=None, options=None):
        raise NotImplementedError


@job
def import_batch(session, model_name, backend_id, filters=None, options=None):
    """ Prepare a batch import of records from Redmine """
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(RedmineBatchImportSynchronizer)
    importer.run(filters=filters, options=options)


@job
def import_record(session, model_name, backend_id, redmine_id, options=None):
    """ Import a record from Redmine """
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(RedmineImportSynchronizer)
    importer.run(redmine_id, options=options)
