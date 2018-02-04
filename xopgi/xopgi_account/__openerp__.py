#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

{
    "name": "Accounting (extended - xopgi)",
    "version": "1.15",
    "author": "Merchise Autrement",
    "website": "http://xopgi.merchise.org/addons/xopgi_account",
    "category": "Accounting",
    "description": "Accounting",
    "depends": ['account_accountant', 'analytic', 'account', ],
    "data": [
        'view/config.xml',
        'view/company.xml',
        'view/account.xml',
        'view/filters.xml',
        'view/reconcile.xml',
        'view/counterpart.xml',
    ],
    "application": False,
    "installable": 10 <= MAJOR_ODOO_VERSION < 11,   # noqa
}
