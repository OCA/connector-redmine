# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo.addons.connector.unit import synchronizer
from odoo.addons.queue_job.job import job
from ..connector import get_environment
from openerp.addons.connector.exception import IDMissingInBackend
from odoo.tools.translate import _
# import odoo.addons.connector.exception as cn_exception

_logger = logging.getLogger(__name__)


class RedmineImporter(synchronizer.Importer):
    """ Base importer for Redmine """

    def __init__(self, environment):
        """
        :param environment: current environment (backend, ...)
        :type environment: :py:class:`connector.connector.ConnectorEnvironment`
        """
        super(RedmineImporter, self).__init__(environment)
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

    def _validate_data(self, data):
        """ Check if the values to import are correct
        Pro-actively check before the ``_create`` or
        ``_update`` if some fields are missing or invalid.
        Raise `cn_exception.InvalidDataError`
        """
        return

    def _must_skip(self):
        """ Hook called right after we read the data from the backend.
        If the method returns a message giving a reason for the
        skipping, the import will be interrupted and the message
        recorded in the job (if the import is called directly by the
        job, not by dependencies).
        If it returns None, the import will continue normally.
        :returns: None | str | unicode
        """
        return

    def _get_binding_id(self):
        """Return the binding id from the redmine id"""
        return self.binder.to_internal(self.redmine_id)

    def _create_data(self, map_record, **kwargs):
        return map_record.values(for_create=True, **kwargs)

    def _create(self, data):
        """ Create the Odoo record """
        # special check on data before import
        self._validate_data(data)
        model = self.model.with_context(connector_no_export=True)
        binding = model.create(data)
        _logger.debug('%s %d created from Redmine %s',
                      self.model._name, binding, self.redmine_id)
        return binding

    def _update_data(self, map_record, **kwargs):
        return map_record.values(**kwargs)

    def _update(self, binding, data):
        """ Update an Odoo record """
        # special check on data before import
        self._validate_data(data)
        binding.with_context(connector_no_export=True).write(data)
        _logger.debug('%s %d updated from Redmine record %s',
                      self.model._name, binding, self.redmine_id)
        return

    def run(self, redmine_id, options=None):
        """ Run the synchronization

        :param redmine_id: identifier of the record on Redmine
        :param options: dict of parameters used by the synchronizer
        """
        self.redmine_id = redmine_id
        try:
            self.redmine_record = self._get_redmine_data()
        except IDMissingInBackend:
            return _('Record does no longer exist in Redmine')

        skip = self._must_skip()
        if skip:
            return skip

        # Case where the redmine record is not found in the backend.
        if self.redmine_record is None:
            return

        binding_id = self._get_binding()

        map_record = self._map_data()
        self.updated_on = map_record.values()['updated_on']

        if binding_id:
            record = self._update_data(map_record)
            self._update(binding_id, record)
        else:
            record = self._create_data(map_record)
            binding_id = self._create(record).id

        self.binder.bind(self.redmine_id, binding_id)

    @property
    def redmine_cache(self):
        return self.connector_env.redmine_cache


class RedmineBatchImporter(synchronizer.Importer):

    def run(self, filters=None, options=None):
        raise NotImplementedError


@job
def import_batch(model_name, backend, filters=None, options=None):
    """ Prepare a batch import of records from Redmine """
    env = get_environment(model_name, backend)
    importer = env.get_connector_unit(RedmineBatchImporter)
    importer.run(filters=filters, options=options)


@job
def import_record(model_name, backend, redmine_id, options=None):
    """ Import a record from Redmine """
    env = get_environment(model_name, backend)
    importer = env.get_connector_unit(RedmineImporter)
    importer.run(redmine_id, options=options)
