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

    "depends": ["base", "account", "sale", "crm", "purchase_requisition",
                "xhg_autrement_project_dossier",
                "xopgi_account_analytic_enhancement"],

    "data": [
        "security/ir.model.access.csv",
        "views/operations_performance_views.xml",
        "workflow/sale_order_workflow.xml",
        "workflow/purchase_order_workflow.xml"
    ],

    "demo": [],

    'installable': (8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa
}
