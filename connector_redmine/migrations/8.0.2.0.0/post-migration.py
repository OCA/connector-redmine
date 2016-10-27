# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, SUPERUSER_ID
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute(
        "SELECT id, redmine_backend_id FROM res_users "
        "WHERE redmine_backend_id IS NOT NULL")

    for uid, redmine_backend_id in cr.fetchall():
        user = env['res.users'].browse(uid)
        user.write({'redmine_backend_ids': [(4, redmine_backend_id)]})

    cr.execute("ALTER TABLE res_users DROP COLUMN redmine_backend_id")
