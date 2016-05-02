{
    'name' : 'Distance Calculator Widget',
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
        'views/distance_calculator.xml',
        "views/travel_routes.xml",
    ],
    'depends' : ['base', 'web'],
    'qweb': ['static/src/xml/distance_calculator.xml'],
    'application': True,
    'installable': True,
    'auto_install': True,
}
