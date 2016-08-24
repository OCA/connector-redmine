# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Redmine Import Time Entry',
    'version': '7.0.2.0.0',
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
