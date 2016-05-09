# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Redmine Import Time Entry',
    'version': '8.0.1.0.0',
    'author': 'Savoir-faire Linux,Odoo Community Association (OCA)',
    'maintainer': 'Odoo Community Association (OCA)',
    'website': 'http://odoo-community.org',
    'category': 'Connector',
    'license': 'AGPL-3',
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
