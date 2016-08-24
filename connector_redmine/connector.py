# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.connector.connector import ConnectorEnvironment
from openerp.addons.connector.checkpoint import checkpoint


def get_environment(session, model_name, backend_id):
    """ Create an environment to work with. """
    backend_record = session.env['redmine.backend'].browse(backend_id)
    env = ConnectorEnvironment(backend_record, session, model_name)
    lang = backend_record.default_lang_id
    lang_code = lang.code if lang else 'en_US'
    session.change_context(lang=lang_code)
    return env


def add_checkpoint(session, model_name, record_id, backend_id):
    return checkpoint.add_checkpoint(
        session, model_name, record_id, 'redmine.backend', backend_id)
