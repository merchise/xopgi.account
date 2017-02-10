# -*- coding: utf-8 -*-


{
    'name': "Invoice Complex Search",

    'summary': "Permite el filtrado de facturas mediante campos hijos de entidades relacionadas. Ej. partner_id.tag",

    'version': '1.0',

    'depends': ['account'],

    'author': "Merchise Autrement",

    'category': 'Accounting & Finance',

    'description': """
    Permite el filtrado de facturas mediante campos hijos de entidades relacionadas.
     - partner_id.tag
    """,

    'data': ['views/invoice.xml'],

    'installable': (8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa

}
