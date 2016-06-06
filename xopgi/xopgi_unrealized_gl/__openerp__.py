# -*- coding: utf-8 -*-
{
    "name": "Unrealized Gain & Loss",

    "summary": ("Genera las entradas correspondientes al cierre para "
                "ganancias y pérdidas basadas en fluctuaciones de moneda"),

    "description": """
        Genera las entradas correspondientes al cierre para ganancias
        y pérdidas basadas en fluctuaciones de moneda
    """,

    "author": "Merchise Autrement",

    "category": "Accounting",

    "version": "1.0",

    "depends": ["base", "account"],

    "data": [
        "views/account_config_settings.xml",
        "wizard/unrealized_gl_wizard.xml"
    ],

    'installable': (8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa
}
