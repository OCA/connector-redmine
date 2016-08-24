Redmine Connector
=================

Base connector module for Redmine.
It Allows to authenticate to a Redmine instance using the REST API.

It also defines a method getUser that searches the Redmine user related
to the Odoo user. The user login must be the same in both systems.


Installation
============

 - Install Redmine
     Refer to http://www.redmine.org/projects/redmine/wiki/redmineinstall

 - Install python-redmine
     sudo pip install python-redmine


Configuration
=============

- Go to Connectors -> Redmine -> Backends
- Create a backend
    - Location: the url of the Redmine service
    - Key: the REST API key of your Redmine instance
- Click on the button to test the connection

You must set one Redmine service as the default one. You must check the box `Default Redmine Service`.
By default, the timesheets of every user will be imported from that redmine service. If a user needs to
import his timesheets from a different redmine service, he may change it in his preference settings,
the same way you switch companies.

Known issues / Roadmap
======================

 - None

Credits
=======

Contributors
------------

.. image:: http://sflx.ca/logo
   :alt: Savoir-faire Linux
   :target: http://www.savoirfairelinux.com

* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* Virgil Dupras <virgil.dupras@savoirfairelinux.com>
* Guillaume Auger <guillaume.auger@savoirfairelinux.com>
* David Dufresne <david.dufresne@savoirfairelinux.com>


Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
