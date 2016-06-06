# -*- coding: utf-8 -*-


{
    "name": "Account Analytic Enhancement",

    "summary": "Adorna las vistas de cuentas analíticas",

    "version": "1.0",

    "depends": [
        "account",
        "account_analytic_analysis",
        'decimal_precision',
    ],

    "author": "Merchise Autrement",

    "category": "Accounting & Finance",

    "description": """
    - Adiciona la columna % de margen a los datos de la cuenta analítica.
    - Adiciona la fecha de caducidad de la cuenta analítica si es de contrato o proyecto.
    """,

    "data": [
        "data/salesperson_wizard_data.xml",
        "views/account_analytic_account_views.xml",
        "wizard/salesperson_wizard.xml"
    ],

    'installable': (8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa

}
