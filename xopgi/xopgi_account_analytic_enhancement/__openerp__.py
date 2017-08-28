# -*- coding: utf-8 -*-

dict(
    name="Account Analytic Enhancement",
    version="1.0",
    depends=list(filter(bool, [
        'account',
        'decimal_precision',
        'account_analytic_analysis' if MAJOR_ODOO_VERSION < 9 else None,  # noqa
    ])),
    author="Merchise Autrement [~º/~]",
    category="Accounting & Finance",

    data=[
        "data/%d/salesperson_wizard_data.xml" % MAJOR_ODOO_VERSION, # noqa
        "views/%d/account_analytic_account_views.xml" % MAJOR_ODOO_VERSION, # noqa
        "wizard/%d/salesperson_wizard.xml" % MAJOR_ODOO_VERSION, # noqa
    ],

    installable=8 <= MAJOR_ODOO_VERSION < 9,   # noqa
)
