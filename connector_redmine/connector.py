# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict
from odoo.addons.connector.connector import ConnectorEnvironment
from odoo.addons.connector.checkpoint import checkpoint


class RedmineEnvironment(ConnectorEnvironment):
    """ Include all the extensions to the environment that this
    adapters of this connector uses (ex. the redmine_cache).
    """
    _propagate_kwargs = ['redmine_cache']

    def __init__(self, backend_record, model_name, redmine_cache=None):
        super(RedmineEnvironment, self).__init__(backend_record,
                                                     model_name)
        self.redmine_cache = redmine_cache or defaultdict(dict)


def get_environment(model_name, backend):
    """ Create an environment to work with. """
    env = RedmineEnvironment(backend, model_name)
    # TODO: look for another way to set default language.
    # session is not available anymore
    # lang = backend_record.default_lang_id
    # lang_code = lang.code if lang else 'en_US'
    # session.change_context(lang=lang_code)
    return env


def add_checkpoint(env, model_name, record_id, backend_id):
    return checkpoint.add_checkpoint(
        env, model_name, record_id, 'redmine.backend', backend_id)
