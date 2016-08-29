.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
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

# Go to Connectors -> Redmine -> Backends

# Create a backend
    - Location: the url of the Redmine service
    - Key: the REST API key of your Redmine instance

# Click on the button to test the connection

Usage
=====

To use this module, you need to:

#. Go to ...

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/169/8.0

Known issues / Roadmap
======================

 - None

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/connector-redmine/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* Virgil Dupras <virgil.dupras@savoirfairelinux.com>
* Guillaume Auger <guillaume.auger@savoirfairelinux.com>
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
