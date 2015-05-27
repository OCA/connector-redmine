# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 - Present Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
from openerp.addons.connector.unit.synchronizer import ImportSynchronizer
from openerp.addons.connector.queue.job import job
from ..import connector


_logger = logging.getLogger(__name__)


class RedmineImportSynchronizer(ImportSynchronizer):
    """ Base importer for Redmine """

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(RedmineImportSynchronizer, self).__init__(environment)
        self.redmine_id = None
        self.updated_on = None

    def _get_redmine_data(self):
        """ Return the raw Redmine data for ``self.redmine_id`` in a dict
        """
        return self.backend_adapter.read(self.redmine_id)

    def _map_data(self):
        """ Returns an instance of
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
        binding_id = self.session.create(self.model._name, data)
        _logger.info(
            '%s %d created from Redmine %s',
            self.model._name, binding_id, self.redmine_id)
        return binding_id

    def _update_data(self, map_record, **kwargs):
        return map_record.values(**kwargs)

    def _update(self, binding_id, data):
        """ Update an OpenERP record """
        self.session.write(self.model._name, binding_id, data)

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

        binding_id = self._get_binding_id()

        map_record = self._map_data()
        self.updated_on = map_record.values()['updated_on']

        if binding_id:
            record = self._update_data(map_record)
            self._update(binding_id, record)
        else:
            record = self._create_data(map_record)
            binding_id = self._create(record)

        self.binder.bind(self.redmine_id, binding_id)


class RedmineBatchImportSynchronizer(ImportSynchronizer):
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
