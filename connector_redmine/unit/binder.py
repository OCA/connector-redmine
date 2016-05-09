# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, ustr
from openerp.addons.connector.connector import Binder
from ..backend import redmine

from datetime import datetime


@redmine
class RedmineModelBinder(Binder):
    _model_name = [
        'redmine.hr.analytic.timesheet',
    ]

    def to_openerp(self, external_id, unwrap=False):
        """ Give the OpenERP ID for an external ID

        :param external_id: external ID for which we want the OpenERP ID
        :param unwrap: if True, returns the openerp_id of the redmine_xxxx
                       record, else return the id (binding id) of that record
        :return: a record ID, depending on the value of unwrap,
                 or None if the external_id is not mapped
        :rtype: int
        """
        with self.session.change_context({'active_test': False}):
            model = self.session.env[self.model._name]
            binding_ids = model.search([
                ('redmine_id', '=', ustr(external_id)),
                ('backend_id', '=', self.backend_record.id)
            ])

        if not binding_ids:
            return None

        binding = binding_ids[0]

        if unwrap:
            return binding.openerp_id.id
        else:
            return binding.id

    def to_backend(self, record_id, wrap=False):
        """ Give the external ID for an OpenERP ID

        :param record_id: OpenERP ID for which we want the external id
        :param wrap: if False, record_id is the ID of the binding,
            if True, record_id is the ID of the normal record, the
            method will search the corresponding binding and returns
            the backend id of the binding
        :return: backend identifier of the record
        """
        if wrap:
            with self.session.change_context({'active_test': False}):
                model = self.session.env[self.model._name]
                erp_record = model.search([
                    ('openerp_id', '=', record_id),
                    ('backend_id', '=', self.backend_record.id),
                ])
            if erp_record:
                return erp_record[0].redmine_id
            else:
                return None

        record = self.session.env[self.model._name].browse(record_id)
        return record.redmine_id

    def bind(self, external_id, binding_id):
        """ Create the link between an external ID and an OpenERP ID and
        update the last synchronization date.

        :param external_id: External ID to bind
        :param binding_id: OpenERP ID to bind
        :type binding_id: int
        """
        # avoid to trigger the export when we modify the `redmine_id`
        context = self.session.context.copy()
        context['connector_no_export'] = True
        now_fmt = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        record = self.session.env[self.model._name].browse(binding_id)

        record.write({
            'redmine_id': ustr(external_id),
            'sync_date': now_fmt
        })

    def unwrap_binding(self, binding_id, browse=False):
        """ For a binding record, gives the normal record.

        Example: when called with a ``redmine.product.product`` id,
        it will return the corresponding ``product.product`` id.

        :param browse: when True, returns a browse_record instance
                       rather than an ID
        :return: the ID of the openerp object
        """
        record = self.session.env[self.model._name].browse(binding_id)
        binding = record.read(['openerp_id'])[0]

        openerp_id = binding['openerp_id'][0]

        if browse:
            model = self.session.env[self.unwrap_model()]
            return model.browse(openerp_id)

        return openerp_id

    def unwrap_model(self):
        """ For a binding model, gives the name of the normal model.

        Example: when called on a binder for ``redmine.product.product``,
        it will return ``product.product``.

        This binder assumes that the normal model lays in ``openerp_id`` since
        this is the field we use in the ``_inherits`` bindings.
        """
        try:
            column = self.model._columns['openerp_id']
        except KeyError:
            raise ValueError('Cannot unwrap model %s, because it has '
                             'no openerp_id field' % self.model._name)
        return column._obj
