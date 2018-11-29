#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

{
    "name": "Account Advancement",
    "version": "1.0",
    "author": "Merchise Autrement",
    "website": "http://xopgi.merchise.org/addons/xopgi_account_advancement",
    "category": "Accounting",
    "description": "Accounting advancement",
    "depends": [
        'account_accountant',
        'analytic',
        'account',
        'xopgi_account',
        'xopgi_proper_currency',
    ],
    "data": [
        'views/advancement.xml',
        'views/invoice.xml',
        'views/config.xml',
        'views/assets.xml',
    ],
    'qweb': [
        "static/src/xml/advanced_payment.xml",
    ],
    "application": False,
    "installable": 10 <= MAJOR_ODOO_VERSION < 11,   # noqa
}
