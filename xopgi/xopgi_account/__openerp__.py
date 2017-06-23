# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi_account.__openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~]
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2013-11-11


{
    "name": "Accounting (extended - xopgi)",
    "version": "1.15",
    "author": "Merchise Autrement",
    "website": "http://xopgi.merchise.org/addons/xopgi_account",
    "category": "Accounting",
    "description": "Accounting",
    "depends": ['account_accountant', 'analytic', 'account', ],
    "data": [
        'view/%d/config.xml' % ODOO_VERSION_INFO[0],  # noqa
        'view/%d/company.xml' % ODOO_VERSION_INFO[0],  # noqa
        'view/%d/account.xml' % ODOO_VERSION_INFO[0],  # noqa
        'view/%d/filters.xml' % ODOO_VERSION_INFO[0],  # noqa
        'view/%d/posting.xml' % ODOO_VERSION_INFO[0],  # noqa
        'view/%d/reconcile.xml' % ODOO_VERSION_INFO[0],  # noqa
        'static/%d/assets.xml' % ODOO_VERSION_INFO[0],  # noqa
    ],
    "application": False,
    "installable": (8, 0) <= ODOO_VERSION_INFO < (10, 0),   # noqa
}
