# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Redmine Connector',
    'version': '8.0.1.0.0',
    'author': 'Savoir-faire Linux,Odoo Community Association (OCA)',
    'maintainer': 'Odoo Community Association (OCA)',
    'website': 'http://odoo-community.org',
    'category': 'Connector',
    'license': 'AGPL-3',
    'depends': [
        'connector',
        'hr_timesheet_sheet',
    ],
    'external_dependencies': {
        'python': ['redmine'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/redmine_backend_view.xml',
        'views/redmine_menu.xml',
        'views/res_users.xml',
    ],
    'application': True,
    'installable': True,
}
