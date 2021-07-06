# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Redmine Connector",
    "version": "12.0.1.0.0",
    "author": "Odoo Community Association (OCA)/Elego Software Solutions GmbH",
    "category": "Connector",
    "website": "https://github.com/OCA/connector-redmine",
    "license": "AGPL-3",
    "depends": [
        "connector",
        "account",
        "hr_timesheet",
        "project",
        "project_task_default_stage",
        "project_task_add_very_high",
    ],
    "external_dependencies": {
        "python": [
            "textile",
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "data/cron_import_issue.xml",
        "views/redmine_backend_view.xml",
        "views/redmine_menu.xml",
        "views/hr_timesheet_view.xml",
        "views/project_views.xml",
    ],
    "application": True,
    "installable": True,
}
