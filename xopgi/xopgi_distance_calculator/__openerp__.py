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
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'data/res.route.points.xml',
        'data/res.routes.xml',
        'views/distance_calculator.xml',
        "views/travel_routes.xml",
    ],
    'qweb': ['static/src/xml/distance_calculator.xml'],
    'application': False,
    'installable': (8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa
    'auto_install': False,
}
