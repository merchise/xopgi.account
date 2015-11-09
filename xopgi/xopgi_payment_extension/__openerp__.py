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
        # "views/account_invoice.xml",-> Commented because there is an existing
        # module with this filter
        "wizard/voucher_wizard.xml"
    ],
}
