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
        "wizard/voucher_wizard.xml"
    ],
}