# -*- coding: utf-8 -*-
{
    "name": "Unrealized Gain & Loss",
    "author": "Merchise Autrement",
    "category": "Accounting",
    "version": "1.0",
    "depends": ["base", "account"],
    "data": [
        "settings/view.xml",
        "wizard/unrealized_gl_wizard.xml"
    ],
    'installable': (8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa
}
