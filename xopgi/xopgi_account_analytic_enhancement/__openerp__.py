# -*- coding: utf-8 -*-

dict(
    name="Account Analytic Enhancement",
    version="1.0",
    depends=(
        [
            'account',
            'decimal_precision',
        ] + (['account_analytic_analysis']
             if ODOO_VERSION_INFO < (9, 0) else [])  # noqa
    ),
    author="Merchise Autrement [~º/~]",
    category="Accounting & Finance",

    data=[
        "data/%d/salesperson_wizard_data.xml" % ODOO_VERSION_INFO[0], # noqa
        "views/%d/account_analytic_account_views.xml" % ODOO_VERSION_INFO[0], # noqa
        "wizard/%d/salesperson_wizard.xml" % ODOO_VERSION_INFO[0], # noqa
    ],

    installable=(8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa
)
