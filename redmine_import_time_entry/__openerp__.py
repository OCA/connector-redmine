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

{
    'name': 'Redmine Import Time Entry',
    'version': '7.0.2.1.0',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux,Odoo Community Association (OCA)',
    'website': 'http://odoo-community.org',
    'category': 'Connector',
    'description': """
Redmine Import Time Entry
=========================
Import time entries from Redmine to the employee's analytic timesheet.
""",
    'depends': [
        'connector_redmine',
    ],
    'external_dependencies': {},
    'data': [
        'data/ir_cron_data.xml',
        'views/redmine_backend_view.xml',
        'views/hr_timesheet_sheet_view.xml',
    ],
    'application': False,
    'installable': True,
    'active': False,
    'js': ['static/src/js/timesheet.js'],
}
