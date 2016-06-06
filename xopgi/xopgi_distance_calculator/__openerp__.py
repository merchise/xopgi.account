{
    'name': 'Distance Calculator Widget',
    'version': '1.0',
    'summary': 'Calculate the distance between cities and places.',
    'author': 'Merchise Autrement',
    'category': 'Accounting',
    'complexity': 'easy',
    'description':
        """
Distance Calculator Widget
====================

Allows users to know the distance between cities and places.
        """,
    'data': [
        'security/ir.model.access.csv',
        'views/distance_calculator.xml',
        "views/travel_routes.xml",
    ],
    'depends': ['base', 'web'],
    'qweb': ['static/src/xml/distance_calculator.xml'],
    'application': False,
    'installable': (8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa
    'auto_install': False,
}
