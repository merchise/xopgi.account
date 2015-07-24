# -*- coding: utf-8 -*-


{
    'name': "Account Analytic Enhancement",

    'summary': "Adorna las vistas de cuentas analíticas",

    'version': '1.0',

    'depends': ['account'],

    'author': "Merchise Autrement",

    'category': 'Accounting & Finance',

    'description': """
    - Adiciona la columna % de margen a los datos de la cuenta analítica.
    - Adiciona la fecha de inicio de la cuenta analítica si es de contrato o proyecto.
    - Adiciona la vista de gráfico a las cuentas analíticas.
    """,

    'data': [
        'views/account_analytic_account_views.xml',
    ],
}
