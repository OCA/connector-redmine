.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Redmine Import Time Entry
=========================

Connector used to import Redmine time entries as Odoo analytic timesheets in batch.

To use this module, you must add a custom field on your Redmine projects. You can give the name you want
to this field, but every project must have a different value for this field.

In Odoo, you must create an analytic account for each Redmine project.
The value of the custom field must be written in the field ref ('Reference') of the analytic account.


Installation
============

Nothing to do.


Configuration
=============

# Go to Connectors -> Redmine -> Backends and select your Redmine backend

# Enter the name of the custom field used to identify projects in Redmine

# Click on the button to test the custom field

# The field "Time Entries - Number of days" is by default set to 14. This means that the connector will
    only fetch time entries that have a date between 2 weeks ago and now. Of course, the connector will only
    create single jobs for Redmine records that have been updated since the last update.

You must set one Redmine service as the default one. For this, you may check the box `Default Redmine Service`.
By default, the timesheets of every user will be imported from that redmine service. If a user needs to
import his timesheets from a different redmine service, he may change it in his preference settings,
the same way you switch companies.

Usage
=====

To use this module, you need to:

#. Go to ...

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/169/8.0

Known issues / Roadmap
======================

The Redmine API does not allow to fetch time entry records based on the last update field.
For this reason, the connector fetches every records for a period of time (e.g. 2 weeks) as explained in Configuration.

Timesheet Entries Update
------------------------
In vanilla Odoo, there is a flaw of design with the timesheet widget. When you modify a time entry using
the widget, instead of updating the existing records, Odoo deletes all records and creates all of them from
the begginning. Not only it has a performance impact, but it also conflicts with the Redmine Connector. This is
why the widget is fixed in this module so that entries are updated intead of recreated.

This issue has another impact. The field partner_id on analytic.timesheet.line is related and it is not readonly.
This is a flaw of design but in vanilla Odoo, it does not cause issues because of the entries are not updated.
Therefore, the field partner_id is set to readonly to prevent access errors.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/connector-redmine/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------
* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* David Dufresne <david.dufresne@savoirfairelinux.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
