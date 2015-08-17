# -*- coding: utf-8 -*-

{
    "name": "Operations Performance Report",

    "summary": """Show performance on operations management""",

    "description": """
        Show performance on operations management:
            - Response time
            - Facturation time
            - Reservation time
    """,

    "author": "Merchise Autrement",

    "category": "Specific Industry Applications",

    "version": "1.0",

    "depends": ["base", "account", "sale", "crm"],

    "data": [
        "views/operations_performance_views.xml"
    ],

    "demo": [],
}
