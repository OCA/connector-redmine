.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=================
Redmine Connector
=================

Base connector module for Redmine.

It allows the authentication to a Redmine instance using the REST API.

It also defines a method getUser that searches for the Redmine user related
to the Odoo user.

Be aware that the user login must be the same in both systems.

Installation
============

# Install Redmine
    Refer to http://www.redmine.org/projects/redmine/wiki/redmineinstall

# Install python-redmine
    sudo pip install python-redmine


Configuration
=============

## Add this to the end of the openerp-server.conf.

    server_wide_modules = web, queue_job
    is_job_channel_available = True

    [queue_job]
    channels = root: 3

## Create a backend

    - Go to Connectors -> Redmine -> Backends
    - Odoo user must be “Job Queue Manager” and “Connector Manager” to create new backends.
    - New backends can be created under Connector / Redmine / Backends.
    - Enter the URL to the Redmine
    - Enter the admin's API key
    - Enter the word "contract_ref" (without quotation marks) in "Contract # field name"
    - For the Redmine projects, the name of the Odoo project must be entered in the field
    - Click on the button to test the connection

## Odoo projects

    - For the Redmine projects to be synchronized, projects must be created in Odoo.
    - The name of the Odoo project must be entered in Redmine under configuration in the “contract_ref” field

## Odoo project stages

    - For the ticket status in Redmine you need Odoo levels.
    - At the levels there is a field for the Redmine status, which should be mapped to this level.
    - The levels must apply to the project.

## Odoo users

    - Create Odoo users who have the same login name as in Redmine or their email address.
    - Create a default user for each project, which will always be assigned to tasks / time records if it is not an Odoo user.
    - This must be entered in the project.

## Odoo employees

    - Create Odoo employees and link them to the Odoo users.
    - If not, the time entries are created without employees

## Notes

    - The project has the "last imported on" field.
    - This does not correspond to the time at which the function was last called in Odoo, but:
    - During the last import, tickets that were last updated in Redmine on a specific date were synchronized.
    - The "latest" date of all these tickets is now "last imported on".
    - Attention : If a time entry is added or changed in Redmine, this does NOT change the “last updated” date of the Redmine ticket!
