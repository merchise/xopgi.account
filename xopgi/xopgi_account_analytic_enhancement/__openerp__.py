# -*- coding: utf-8 -*-

dict(
    name="Account Analytic Enhancement",
    version="1.0",
    depends=list(filter(bool, [
        'account',
        'decimal_precision',
        'analytic',
        'sales_team',
        'xopgi_analytic_parent',
        'xopgi_analytic_state',
        'xopgi_analytic_manager',
        'xopgi_analytic_sale_contracts',
    ])),
    author="Merchise Autrement [~º/~]",
    category="Accounting & Finance",

    data=[
        "data/salesperson_wizard_data.xml",
        "views/account_analytic_account_views.xml",
        "wizard/salesperson_wizard.xml",
    ],

    installable=10 <= MAJOR_ODOO_VERSION < 11,   # noqa
)
