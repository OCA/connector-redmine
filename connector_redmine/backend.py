# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.addons.connector.backend as backend


redmine = backend.Backend('redmine')
""" Generic Redmine Backend """

redmine13 = backend.Backend(parent=redmine, version='1.3')
""" Redmine Backend for version 1.3 and up """
