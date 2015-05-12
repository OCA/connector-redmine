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

from openerp.osv import orm
from openerp.tools.translate import _
from openerp.addons.connector.session import ConnectorSession
from ..unit.import_synchronizer import import_single_user_time_entries


class HrTimesheetSheet(orm.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    def import_timesheets_from_redmine(self, cr, uid, ids, context=None):
        timesheet = self.browse(cr, uid, ids[0], context=context)

        session = ConnectorSession(cr, uid, context)
        backend_ids = self.pool['redmine.backend'].search(
            cr, uid, [('time_entry_import_activate', '=', True)],
            context=context)

        if not backend_ids:
            return

        backend_id = backend_ids[0]

        employee = timesheet.employee_id

        if not employee:
            raise orm.except_orm(
                _('Error!'),
                _('The employee %s is not related to a user') % employee.name)

        import_single_user_time_entries(
            session, backend_id, employee.user_id.login,
            timesheet.date_from, timesheet.date_to)
