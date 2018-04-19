import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-connector-redmine",
    description="Meta package for oca-connector-redmine Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-connector_redmine',
        'odoo8-addon-redmine_import_time_entry',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
