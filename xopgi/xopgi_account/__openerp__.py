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
        'view/%d/config.xml' % MAJOR_ODOO_VERSION,  # noqa
        'view/%d/company.xml' % MAJOR_ODOO_VERSION,  # noqa
        'view/%d/account.xml' % MAJOR_ODOO_VERSION,  # noqa
        'view/%d/filters.xml' % MAJOR_ODOO_VERSION,  # noqa
        'view/%d/posting.xml' % MAJOR_ODOO_VERSION,  # noqa

        'view/reconcile.xml',

        'static/%d/assets.xml' % MAJOR_ODOO_VERSION,  # noqa
    ],
    "application": False,
    "installable": 8 <= MAJOR_ODOO_VERSION < 11,   # noqa
}
