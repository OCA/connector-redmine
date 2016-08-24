# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict
from openerp.addons.connector.session import ConnectorSession


class RedmineConnectorSession(ConnectorSession):

    def __init__(self, cr, uid, context=None):
        super(RedmineConnectorSession, self).__init__(cr, uid, context)
        self.redmine_cache = defaultdict(dict)
