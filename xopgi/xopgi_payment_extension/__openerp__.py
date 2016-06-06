# -*- coding: utf-8 -*-
{
    'name': "Payment Extensions",

    'summary': """
        Set payment enhancement and usability""",

    'description': """
        Set payment enhancement and usability
    """,

    "author": "Merchise Autrement",

    'category': 'Accounting & Finance',
    'version': '1.0',

    'depends': ['base', "account_voucher"],

    'data': [
        # 'security/ir.model.access.csv',
        "views/account_voucher_views.xml",
        "wizard/voucher_wizard.xml"
    ],

    'installable': (8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa

}
