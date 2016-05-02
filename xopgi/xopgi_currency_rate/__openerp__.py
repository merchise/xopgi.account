{
    'name' : 'Currency Exchange Rate Converter Widget',
    'version': '1.0',
    'summary': 'Show currency exchange an provide a converter.',
    'author': 'Merchise Autrement',
    'category': 'Accounting',
    'complexity': 'easy',
    'description':
        """
Currency Exchange Rate Converter Widget
====================

Allows users to know the currency exchange an provide a converter with the lastest updated currency rate.
        """,
    'data': [
        'views/currency_rate.xml',
    ],
    'depends' : ['base', 'web'],
    'qweb': ['static/src/xml/currency_rate.xml'],
    'application': True,
    'installable': True,
    'auto_install': True,
}
