#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

{
    'name': 'Create statements from payments/entries',
    'version': '1.0',
    'author': 'Merchise Autrement',
    'category': 'Accounting',
    'description': 'Create statements from payments/entries',
    'depends': [
        'account',

        # Use the line_currency_amount that is defined here
        'xopgi_proper_currency',
    ],
    'data': [
        'views/filters.xml',
        'views/payments.xml',
    ],
    'application': False,
    'installable': 10 <= MAJOR_ODOO_VERSION < 12,   # noqa
}
